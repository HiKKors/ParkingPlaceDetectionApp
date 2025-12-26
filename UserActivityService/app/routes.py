from flask import Blueprint, render_template, request
from .extensions import db
from .user_activity_logger import activity_logger
from .models import Feedback

activity_bp = Blueprint('activity', __name__)

@activity_bp.route('/send-feedback', methods=['GET', 'POST'])
def feedback_form():
    if request.method == 'GET':
        return render_template('feedback_form.html')
    elif request.method == 'POST':
        feedback = request.form['feedback']
        new_feedback = Feedback(feedback=feedback)
        try:
            db.session.add(new_feedback)
            db.session.commit()
            activity_logger.info('Успешно добавлен отзыв')
        except Exception as e:
            activity_logger.error('Ошибка при добавлении отзыва: %s', str(e))
            return {'Ошибка': str(e)}


