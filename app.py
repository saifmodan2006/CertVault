import os, uuid, io, base64, sqlite3
from datetime import datetime, date, timedelta
from functools import wraps
from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, send_from_directory, jsonify, abort)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from PIL import Image, ImageDraw
import re

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'certvault-super-secret-key-2024-xK9pL')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['DB_PATH'] = os.environ.get('DB_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'certvault.db'))

# Email Configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False') == 'True'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@certvault.com')
app.config['MAIL_SUPPRESS_SEND'] = os.environ.get('MAIL_SUPPRESS_SEND', 'False') == 'True'

mail = Mail(app)
serializer = URLSafeTimedSerializer(app.secret_key)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_db():
    conn = sqlite3.connect(app.config['DB_PATH'])
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    with get_db() as conn:
        conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            bio TEXT DEFAULT '',
            is_admin INTEGER DEFAULT 0,
            email_verified INTEGER DEFAULT 0,
            verification_token TEXT DEFAULT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS certificates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            issuer TEXT NOT NULL,
            description TEXT DEFAULT '',
            issue_date TEXT NOT NULL,
            expiry_date TEXT,
            tags TEXT DEFAULT '',
            file_path TEXT,
            file_type TEXT DEFAULT '',
            unique_id TEXT UNIQUE NOT NULL,
            is_public INTEGER DEFAULT 0,
            category TEXT DEFAULT 'General',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            details TEXT DEFAULT '',
            ip_address TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_cert_user_created ON certificates(user_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_cert_user_category ON certificates(user_id, category);
        CREATE INDEX IF NOT EXISTS idx_cert_user_public ON certificates(user_id, is_public);
        CREATE INDEX IF NOT EXISTS idx_logs_user_created ON activity_logs(user_id, created_at DESC);
        ''')
        conn.commit()

def allowed_file(fn):
    return '.' in fn and fn.rsplit('.',1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def send_certificate_notification(user_email, user_name, cert_title):
    """Send certificate upload notification email"""
    try:
        msg = Message(
            subject=f'CertVault - Certificate Added Successfully 🎓',
            recipients=[user_email],
            html=f'''
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #f8f9fa; border-radius: 10px;">
                <h2 style="color: #333;">Certificate Added Successfully!</h2>
                <p style="color: #666; font-size: 16px;">Hi <strong>{user_name}</strong>,</p>
                <p style="color: #666; font-size: 16px;">Your certificate <strong>"{cert_title}"</strong> has been successfully added to CertVault.</p>

                <div style="background: #fff; padding: 15px; border-left: 4px solid #6c5ce7; margin: 20px 0;">
                    <p style="color: #666; margin: 5px 0;">✓ Certificate stored securely</p>
                    <p style="color: #666; margin: 5px 0;">✓ You can manage and share it anytime</p>
                    <p style="color: #666; margin: 5px 0;">✓ Set expiry alerts to never miss renewal</p>
                </div>

                <a href="{url_for('certificates', _external=True)}" style="display: inline-block; background: #6c5ce7; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold;">View Your Certificates</a>

                <p style="color: #999; font-size: 12px; margin-top: 20px;">CertVault - Secure Certificate Management</p>
            </div>
            '''
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def send_password_changed_email(user_email, user_name):
    """Send password change notification email"""
    try:
        msg = Message(
            subject='CertVault - Password Changed 🔐',
            recipients=[user_email],
            html=f'''
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #f8f9fa; border-radius: 10px;">
                <h2 style="color: #333;">Password Changed Successfully</h2>
                <p style="color: #666; font-size: 16px;">Hi <strong>{user_name}</strong>,</p>
                <p style="color: #666; font-size: 16px;">Your password has been changed successfully. If you didn't make this change, please contact our support team immediately.</p>

                <a href="{url_for('profile', _external=True)}" style="display: inline-block; background: #6c5ce7; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold;">Account Settings</a>

                <p style="color: #999; font-size: 12px; margin-top: 20px;">CertVault - Secure Certificate Management</p>
            </div>
            '''
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def login_required(f):
    @wraps(f)
    def d(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue.','warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return d

def get_current_user():
    if 'user_id' not in session: return None
    with get_db() as conn:
        return conn.execute('SELECT * FROM users WHERE id=?',(session['user_id'],)).fetchone()

def log_activity(user_id, action, details=''):
    try:
        with get_db() as conn:
            conn.execute('INSERT INTO activity_logs (user_id,action,details,ip_address) VALUES (?,?,?,?)',
                         (user_id, action, details, request.remote_addr))
            conn.commit()
    except: pass

def auto_categorize(title, tags, issuer):
    text = f"{title} {tags} {issuer}".lower()
    cats = {
        'Technology': ['programming','python','java','aws','cloud','data','ai','ml','cyber',
                       'network','software','it','tech','developer','web','devops','linux'],
        'Business':   ['management','leadership','business','mba','finance','marketing',
                       'project','agile','scrum','pmp','accounting','sales'],
        'Healthcare': ['medical','health','nursing','clinical','hospital','first aid','cpr'],
        'Education':  ['teaching','education','training','course','degree','diploma',
                       'bachelor','master','phd','university','college','academic'],
        'Design':     ['design','photoshop','illustrator','figma','ui','ux','graphic'],
        'Language':   ['english','spanish','french','german','ielts','toefl','language'],
    }
    for cat, keywords in cats.items():
        if any(kw in text for kw in keywords): return cat
    return 'General'

def parse_date(s):
    if not s: return None
    try: return datetime.strptime(str(s)[:10],'%Y-%m-%d').date()
    except: return None

def days_until_expiry(expiry_str):
    d = parse_date(expiry_str)
    return (d - date.today()).days if d else None

def fmt_date(s):
    d = parse_date(s)
    return d.strftime('%B %d, %Y') if d else (s or '')

def fmt_month(s):
    if not s: return ''
    try: return datetime.strptime(str(s)[:7],'%Y-%m').strftime('%b %Y')
    except: return s

def is_expired(expiry_str):
    d = parse_date(expiry_str)
    return d < date.today() if d else False

def is_expiring_soon(expiry_str):
    days = days_until_expiry(expiry_str)
    return days is not None and 0 <= days <= 30

def get_tag_list(tags_str):
    return [t.strip() for t in (tags_str or '').split(',') if t.strip()]

def make_qr_png(data):
    import qrcode
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=(108,92,231), back_color=(255,255,255))
    return img.resize((220,220))

@app.context_processor
def inject_globals():
    return {'current_user':get_current_user(),'now':datetime.utcnow(),
            'fmt_date':fmt_date,'days_until_expiry':days_until_expiry,
            'is_expired':is_expired,'is_expiring_soon':is_expiring_soon,'get_tag_list':get_tag_list}

@app.route('/')
def index():
    with get_db() as conn:
        tc=conn.execute('SELECT COUNT(*) FROM certificates').fetchone()[0]
        tu=conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    user=get_current_user()
    mt=0
    if user:
        with get_db() as conn:
            mt=conn.execute('SELECT COUNT(*) FROM certificates WHERE user_id=?',(user['id'],)).fetchone()[0]
    return render_template('index.html',user=user,total_certs=tc,total_users=tu,stats={'total':mt})

@app.route('/register',methods=['GET','POST'])
def register():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    if request.method=='POST':
        name=request.form.get('name','').strip()
        email=request.form.get('email','').strip().lower()
        pw=request.form.get('password','')
        confirm=request.form.get('confirm_password','')

        # Validation
        if not all([name,email,pw]):
            flash('All fields required.','danger')
            return render_template('register.html')

        if len(name) < 2:
            flash('Name must be at least 2 characters.','danger')
            return render_template('register.html')

        if not is_valid_email(email):
            flash('Please enter a valid email address.','danger')
            return render_template('register.html')

        if pw!=confirm:
            flash('Passwords do not match.','danger')
            return render_template('register.html')

        if len(pw)<8:
            flash('Password must be at least 8 characters.','danger')
            return render_template('register.html')

        # Check password strength
        if not (any(c.isupper() for c in pw) and any(c.isdigit() for c in pw)):
            flash('Password must contain uppercase letters and numbers.','danger')
            return render_template('register.html')

        with get_db() as conn:
            if conn.execute('SELECT id FROM users WHERE email=?',(email,)).fetchone():
                flash('Email already registered.','danger')
                return render_template('register.html')

            count=conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
            cur=conn.execute('INSERT INTO users (name,email,password_hash,is_admin,email_verified) VALUES (?,?,?,?,?)',
                             (name,email,generate_password_hash(pw),1 if count==0 else 0, 1))
            conn.commit()
            uid=cur.lastrowid

        log_activity(uid,'REGISTER',f'New account: {email}')
        flash(f'Welcome, {name}! 🎉 Account created successfully. You can now login!','success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login',methods=['GET','POST'])
def login():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    if request.method=='POST':
        email=request.form.get('email','').strip().lower()
        pw=request.form.get('password','')
        with get_db() as conn:
            user=conn.execute('SELECT * FROM users WHERE email=?',(email,)).fetchone()
        if user and check_password_hash(user['password_hash'],pw):
            session['user_id']=user['id']
            session['user_name']=user['name']
            log_activity(user['id'],'LOGIN',f'IP:{request.remote_addr}')
            flash(f'Welcome back, {user["name"]}! 👋','success')
            return redirect(request.args.get('next') or url_for('dashboard'))
        flash('Invalid email or password.','danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    uid=session.get('user_id')
    if uid: log_activity(uid,'LOGOUT','')
    session.clear(); flash('Logged out.','info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    uid=session['user_id']
    with get_db() as conn:
        certs=conn.execute('SELECT * FROM certificates WHERE user_id=? ORDER BY created_at DESC',(uid,)).fetchall()
        logs=conn.execute('SELECT * FROM activity_logs WHERE user_id=? ORDER BY created_at DESC LIMIT 10',(uid,)).fetchall()
        user=conn.execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone()
    expiring=[c for c in certs if is_expiring_soon(c['expiry_date'])]
    expired=[c for c in certs if is_expired(c['expiry_date'])]
    cats={}
    for c in certs: cats[c['category']]=cats.get(c['category'],0)+1
    pub=sum(1 for c in certs if c['is_public'])
    return render_template('dashboard.html',user=user,certs=certs,expiring=expiring,
                           expired=expired,recent=list(certs[:6]),categories=cats,
                           public_count=pub,private_count=len(certs)-pub,logs=logs)

@app.route('/certificates')
@login_required
def certificates():
    uid=session['user_id']
    q=request.args.get('q',''); category=request.args.get('category','')
    status=request.args.get('status',''); sort_by=request.args.get('sort','newest')
    with get_db() as conn:
        user=conn.execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone()
        sql='SELECT * FROM certificates WHERE user_id=?'; params=[uid]
        if q: sql+=' AND (title LIKE ? OR issuer LIKE ? OR tags LIKE ?)'; params+=[f'%{q}%']*3
        if category: sql+=' AND category=?'; params.append(category)
        sql+=({'oldest':' ORDER BY created_at ASC','title':' ORDER BY title ASC'}).get(sort_by,' ORDER BY created_at DESC')
        certs=conn.execute(sql,params).fetchall()
        all_cats=conn.execute('SELECT DISTINCT category FROM certificates WHERE user_id=?',(uid,)).fetchall()
    if status=='expired': certs=[c for c in certs if is_expired(c['expiry_date'])]
    elif status=='expiring': certs=[c for c in certs if is_expiring_soon(c['expiry_date'])]
    elif status=='active': certs=[c for c in certs if not is_expired(c['expiry_date'])]
    cats=[r['category'] for r in all_cats if r['category']]
    return render_template('certificates.html',user=user,certs=certs,categories=cats,
                           q=q,selected_cat=category,selected_status=status,sort=sort_by)

@app.route('/upload',methods=['GET','POST'])
@login_required
def upload():
    uid=session['user_id']
    with get_db() as conn:
        user=conn.execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone()
    if request.method=='POST':
        title=request.form.get('title','').strip()
        issuer=request.form.get('issuer','').strip()
        description=request.form.get('description','').strip()
        issue_date=request.form.get('issue_date','')
        expiry_date=request.form.get('expiry_date','') or None
        tags=request.form.get('tags','').strip()
        is_public=1 if request.form.get('is_public')=='on' else 0

        if not all([title,issuer,issue_date]):
            flash('Title, Issuer and Issue Date required.','danger')
            return render_template('upload.html',user=user)

        if not issue_date:
            flash('Please provide a valid issue date.','danger')
            return render_template('upload.html',user=user)

        if expiry_date and expiry_date < issue_date:
            flash('Expiry date cannot be before issue date.','danger')
            return render_template('upload.html',user=user)

        cert_uid=str(uuid.uuid4())
        category=auto_categorize(title,tags,issuer)
        file_path=None
        file_type=''
        file=request.files.get('certificate_file')

        if file and file.filename and allowed_file(file.filename):
            ext=file.filename.rsplit('.',1)[1].lower()
            fname=f"{cert_uid}.{ext}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],fname))
            file_path=fname
            file_type=ext

        with get_db() as conn:
            cur=conn.execute(
                '''INSERT INTO certificates
                   (user_id,title,issuer,description,issue_date,expiry_date,tags,
                    file_path,file_type,unique_id,is_public,category)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                (uid,title,issuer,description,issue_date,expiry_date,tags,
                 file_path,file_type,cert_uid,is_public,category))
            conn.commit()
            cid=cur.lastrowid

        # Send certificate upload notification email
        send_certificate_notification(user['email'], user['name'], title)

        log_activity(uid,'UPLOAD',f'Uploaded: {title}')
        flash(f'Certificate uploaded! 🎓','success')
        return redirect(url_for('certificate_detail',cid=cid))
    return render_template('upload.html',user=user)

@app.route('/certificate/<int:cid>')
@login_required
def certificate_detail(cid):
    uid=session['user_id']
    with get_db() as conn:
        cert=conn.execute('SELECT * FROM certificates WHERE id=?',(cid,)).fetchone()
        user=conn.execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone()
    if not cert: abort(404)
    if cert['user_id']!=uid and not user['is_admin']: abort(403)
    # Add share_url to cert dictionary so template can access it
    cert = dict(cert)
    cert['share_url']=url_for('share_certificate',uid=cert['unique_id'],_external=True)
    return render_template('certificate_detail.html',user=user,cert=cert)

@app.route('/certificate/<int:cid>/edit',methods=['GET','POST'])
@login_required
def edit_certificate(cid):
    uid=session['user_id']
    with get_db() as conn:
        cert=conn.execute('SELECT * FROM certificates WHERE id=?',(cid,)).fetchone()
        user=conn.execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone()
    if not cert: abort(404)
    if cert['user_id']!=uid and not user['is_admin']: abort(403)
    if request.method=='POST':
        title=request.form.get('title','').strip()
        issuer=request.form.get('issuer','').strip()
        description=request.form.get('description','').strip()
        issue_date=request.form.get('issue_date','')
        expiry_date=request.form.get('expiry_date','') or None
        tags=request.form.get('tags','').strip()
        is_public=1 if request.form.get('is_public')=='on' else 0
        category=auto_categorize(title,tags,issuer)
        fp=cert['file_path']; ft=cert['file_type']
        file=request.files.get('certificate_file')
        if file and file.filename and allowed_file(file.filename):
            if cert['file_path']:
                old=os.path.join(app.config['UPLOAD_FOLDER'],cert['file_path'])
                if os.path.exists(old): os.remove(old)
            ext=file.filename.rsplit('.',1)[1].lower()
            fname=f"{cert['unique_id']}.{ext}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],fname))
            fp=fname; ft=ext
        with get_db() as conn:
            conn.execute(
                '''UPDATE certificates SET title=?,issuer=?,description=?,issue_date=?,
                   expiry_date=?,tags=?,is_public=?,category=?,file_path=?,file_type=?,
                   updated_at=datetime('now') WHERE id=?''',
                (title,issuer,description,issue_date,expiry_date,tags,is_public,category,fp,ft,cid))
            conn.commit()
        log_activity(uid,'EDIT',f'Edited: {title}')
        flash('Certificate updated! ✅','success')
        return redirect(url_for('certificate_detail',cid=cid))
    return render_template('edit_certificate.html',user=user,cert=cert)

@app.route('/certificate/<int:cid>/delete',methods=['POST'])
@login_required
def delete_certificate(cid):
    uid=session['user_id']
    with get_db() as conn:
        cert=conn.execute('SELECT * FROM certificates WHERE id=?',(cid,)).fetchone()
        user=conn.execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone()
    if not cert: abort(404)
    if cert['user_id']!=uid and not user['is_admin']: abort(403)
    if cert['file_path']:
        fp=os.path.join(app.config['UPLOAD_FOLDER'],cert['file_path'])
        if os.path.exists(fp): os.remove(fp)
    log_activity(uid,'DELETE',f'Deleted: {cert["title"]}')
    with get_db() as conn:
        conn.execute('DELETE FROM certificates WHERE id=?',(cid,)); conn.commit()
    flash('Certificate deleted.','info')
    return redirect(url_for('certificates'))

@app.route('/share/<uid>')
def share_certificate(uid):
    with get_db() as conn:
        cert=conn.execute('SELECT * FROM certificates WHERE unique_id=?',(uid,)).fetchone()
    if not cert: abort(404)
    if not cert['is_public']:
        cu=get_current_user()
        if not cu or cu['id']!=cert['user_id']: abort(403)
    return render_template('share.html',cert=cert)

@app.route('/download/<int:cid>')
@login_required
def download_certificate(cid):
    uid=session['user_id']
    with get_db() as conn:
        cert=conn.execute('SELECT * FROM certificates WHERE id=?',(cid,)).fetchone()
        user=conn.execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone()
    if not cert: abort(404)
    if cert['user_id']!=uid and not user['is_admin']: abort(403)
    if not cert['file_path']:
        flash('No file attached.','warning'); return redirect(url_for('certificate_detail',cid=cid))
    log_activity(uid,'DOWNLOAD',f'Downloaded: {cert["title"]}')
    return send_from_directory(app.config['UPLOAD_FOLDER'],cert['file_path'],
                               as_attachment=True,download_name=f"{cert['title']}.{cert['file_type']}")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

@app.route('/api/qr/<int:cid>')
@login_required
def generate_qr(cid):
    uid=session['user_id']
    with get_db() as conn:
        cert=conn.execute('SELECT * FROM certificates WHERE id=?',(cid,)).fetchone()
        user=conn.execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone()
    if not cert or(cert['user_id']!=uid and not user['is_admin']): return jsonify({'error':'Not found'}),404
    share_url=url_for('share_certificate',uid=cert['unique_id'],_external=True)
    img=make_qr_png(share_url)
    buf=io.BytesIO(); img.save(buf,format='PNG'); buf.seek(0)
    b64=base64.b64encode(buf.getvalue()).decode()
    return jsonify({'qr':f'data:image/png;base64,{b64}','url':share_url})

@app.route('/api/toggle-privacy/<int:cid>',methods=['POST'])
@login_required
def toggle_privacy(cid):
    uid=session['user_id']
    with get_db() as conn:
        cert=conn.execute('SELECT * FROM certificates WHERE id=?',(cid,)).fetchone()
        if not cert or cert['user_id']!=uid: return jsonify({'error':'Unauthorized'}),403
        new_val=0 if cert['is_public'] else 1
        conn.execute('UPDATE certificates SET is_public=? WHERE id=?',(new_val,cid)); conn.commit()
    log_activity(uid,'PRIVACY',f'{"Public" if new_val else "Private"}: {cert["title"]}')
    share_url=url_for('share_certificate',uid=cert['unique_id'],_external=True) if new_val else None
    return jsonify({'is_public':bool(new_val),'share_url':share_url})

@app.route('/api/stats')
@login_required
def api_stats():
    uid=session['user_id']
    with get_db() as conn:
        certs=conn.execute('SELECT * FROM certificates WHERE user_id=?',(uid,)).fetchall()
    monthly={}; cats={}; exp_count=0
    for c in certs:
        created=c['created_at']
        if created:
            try:
                key=datetime.strptime(created[:7],'%Y-%m').strftime('%b %Y')
                monthly[key]=monthly.get(key,0)+1
            except: pass
        cat=c['category'] or 'General'
        cats[cat]=cats.get(cat,0)+1
        if is_expiring_soon(c['expiry_date']): exp_count+=1
    return jsonify({'monthly':monthly,'categories':cats,'total':len(certs),
                    'public':sum(1 for c in certs if c['is_public']),'expiring':exp_count})

@app.route('/profile',methods=['GET','POST'])
@login_required
def profile():
    uid=session['user_id']
    if request.method=='POST':
        action=request.form.get('action')
        with get_db() as conn:
            user=conn.execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone()
        if action=='update_profile':
            name=request.form.get('name','').strip() or user['name']
            bio=request.form.get('bio','').strip()
            with get_db() as conn:
                conn.execute('UPDATE users SET name=?,bio=? WHERE id=?',(name,bio,uid)); conn.commit()
            session['user_name']=name; flash('Profile updated! ✅','success')
        elif action=='change_password':
            cur_pw=request.form.get('current_password','')
            new_pw=request.form.get('new_password','')
            confirm=request.form.get('confirm_password','')

            if not check_password_hash(user['password_hash'],cur_pw):
                flash('Current password incorrect.','danger')
            elif new_pw!=confirm:
                flash('New passwords do not match.','danger')
            elif len(new_pw)<8:
                flash('Password must be at least 8 characters.','danger')
            elif not (any(c.isupper() for c in new_pw) and any(c.isdigit() for c in new_pw)):
                flash('Password must contain uppercase letters and numbers.','danger')
            else:
                with get_db() as conn:
                    conn.execute('UPDATE users SET password_hash=? WHERE id=?',(generate_password_hash(new_pw),uid))
                    conn.commit()

                log_activity(uid,'PASSWORD_CHANGE','Changed password')

                # Send password change notification email
                send_password_changed_email(user['email'], user['name'])

                flash('Password changed! 🔐','success')
        return redirect(url_for('profile'))
    with get_db() as conn:
        user=conn.execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone()
        total=conn.execute('SELECT COUNT(*) FROM certificates WHERE user_id=?',(uid,)).fetchone()[0]
        pub=conn.execute('SELECT COUNT(*) FROM certificates WHERE user_id=? AND is_public=1',(uid,)).fetchone()[0]
        logs=conn.execute('SELECT * FROM activity_logs WHERE user_id=? ORDER BY created_at DESC LIMIT 20',(uid,)).fetchall()
    return render_template('profile.html',user=user,total=total,public=pub,logs=logs)

@app.route('/admin')
@login_required
def admin():
    uid=session['user_id']
    with get_db() as conn:
        user=conn.execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone()
        if not user['is_admin']: abort(403)
        users=conn.execute(
            'SELECT u.*,(SELECT COUNT(*) FROM certificates WHERE user_id=u.id) as cert_count FROM users u ORDER BY u.created_at DESC'
        ).fetchall()
        tc=conn.execute('SELECT COUNT(*) FROM certificates').fetchone()[0]
        tu=conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        logs=conn.execute(
            'SELECT l.*,u.name as uname FROM activity_logs l JOIN users u ON l.user_id=u.id ORDER BY l.created_at DESC LIMIT 20'
        ).fetchall()
    sz=sum(os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'],f))
           for f in os.listdir(app.config['UPLOAD_FOLDER'])
           if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'],f)))
    return render_template('admin.html',user=user,users=users,total_certs=tc,total_users=tu,
                           recent_logs=logs,storage_mb=round(sz/(1024*1024),2))

@app.route('/admin/user/<int:tid>/delete',methods=['POST'])
@login_required
def admin_delete_user(tid):
    uid=session['user_id']
    with get_db() as conn:
        user=conn.execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone()
        if not user['is_admin']: abort(403)
        if tid==uid: flash('Cannot delete yourself.','danger'); return redirect(url_for('admin'))
        certs=conn.execute('SELECT file_path FROM certificates WHERE user_id=?',(tid,)).fetchall()
        for c in certs:
            if c['file_path']:
                fp=os.path.join(app.config['UPLOAD_FOLDER'],c['file_path'])
                if os.path.exists(fp): os.remove(fp)
        conn.execute('DELETE FROM users WHERE id=?',(tid,)); conn.commit()
    flash('User deleted.','success'); return redirect(url_for('admin'))

# ─── Jinja2 Filters ───────────────────────────────────────────

@app.template_filter('fmtdate')
def fmtdate_filter(s, fmt='%B %d, %Y'):
    """Format a date string or date object."""
    if not s: return ''
    if hasattr(s, 'strftime'): return s.strftime(fmt)
    try: return datetime.strptime(str(s)[:10], '%Y-%m-%d').strftime(fmt)
    except: return str(s)

@app.template_filter('fmtdatetime')
def fmtdatetime_filter(s, fmt='%b %d, %H:%M'):
    if not s: return ''
    if hasattr(s, 'strftime'): return s.strftime(fmt)
    try: return datetime.strptime(str(s)[:16], '%Y-%m-%dT%H:%M').strftime(fmt)
    except:
        try: return datetime.strptime(str(s)[:16], '%Y-%m-%d %H:%M').strftime(fmt)
        except: return str(s)[:16]

@app.template_filter('fmtmonth')
def fmtmonth_filter(s):
    if not s: return ''
    if hasattr(s, 'strftime'): return s.strftime('%b %Y')
    try: return datetime.strptime(str(s)[:10], '%Y-%m-%d').strftime('%b %Y')
    except: return str(s)

@app.errorhandler(404)
def not_found(e): return render_template('error.html',code=404,message='Page not found'),404
@app.errorhandler(403)
def forbidden(e): return render_template('error.html',code=403,message='Access forbidden'),403

if __name__=='__main__':
    init_db()
    app.run(debug=True,host='0.0.0.0',port=5000)
