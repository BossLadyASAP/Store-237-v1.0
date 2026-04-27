from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db, Store, User, TeamMember

team_bp = Blueprint('team', __name__, url_prefix='/team')

@team_bp.route('/')
@login_required
def list_team():
    """List team members."""
    stores = Store.query.filter_by(owner_id=current_user.id).all()
    
    if not stores:
        return render_template('no_stores.html')
    
    store = stores[0]
    team_members = TeamMember.query.filter_by(store_id=store.id).all()
    
    return render_template('team.html', store=store, stores=stores, team_members=team_members)

@team_bp.route('/invite', methods=['GET', 'POST'])
@login_required
def invite_member():
    """Invite a team member."""
    stores = Store.query.filter_by(owner_id=current_user.id).all()
    
    if not stores:
        return redirect(url_for('dashboard.dashboard'))
    
    if request.method == 'POST':
        store_id = request.form.get('store_id', type=int)
        email = request.form.get('email')
        role = request.form.get('role', 'viewer')
        
        store = Store.query.get(store_id)
        if not store or store.owner_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if not user:
            # Create new user with temporary password
            user = User(
                username=email.split('@')[0],
                email=email,
                full_name=email
            )
            user.set_password('temp_password_123')
            db.session.add(user)
            db.session.flush()
        
        # Check if already a team member
        existing = TeamMember.query.filter_by(user_id=user.id, store_id=store_id).first()
        if existing:
            return jsonify({'error': 'User is already a team member'}), 400
        
        # Add team member
        team_member = TeamMember(
            user_id=user.id,
            store_id=store_id,
            role=role
        )
        db.session.add(team_member)
        db.session.commit()
        
        return redirect(url_for('team.list_team'))
    
    store = stores[0]
    return render_template('invite_member.html', store=store, stores=stores)

@team_bp.route('/<int:member_id>/role', methods=['POST'])
@login_required
def update_member_role(member_id):
    """Update team member role."""
    member = TeamMember.query.get(member_id)
    
    if not member:
        return jsonify({'error': 'Not found'}), 404
    
    store = Store.query.get(member.store_id)
    if store.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    role = request.form.get('role')
    if role not in ['admin', 'manager', 'viewer']:
        return jsonify({'error': 'Invalid role'}), 400
    
    member.role = role
    db.session.commit()
    
    return redirect(url_for('team.list_team'))

@team_bp.route('/<int:member_id>/remove', methods=['POST'])
@login_required
def remove_member(member_id):
    """Remove a team member."""
    member = TeamMember.query.get(member_id)
    
    if not member:
        return jsonify({'error': 'Not found'}), 404
    
    store = Store.query.get(member.store_id)
    if store.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(member)
    db.session.commit()
    
    return redirect(url_for('team.list_team'))

@team_bp.route('/api/list/<int:store_id>')
@login_required
def api_list_team(store_id):
    """API endpoint to list team members."""
    store = Store.query.get(store_id)
    
    if not store or store.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    members = TeamMember.query.filter_by(store_id=store_id).all()
    
    data = [
        {
            'id': m.id,
            'userName': m.user.username,
            'email': m.user.email,
            'role': m.role,
            'joinedAt': m.joined_at.strftime('%Y-%m-%d')
        }
        for m in members
    ]
    
    return jsonify(data)
