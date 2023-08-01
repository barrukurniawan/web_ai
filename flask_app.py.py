from flask import Flask, request
from bardapi import Bard
from flask_sqlalchemy import SQLAlchemy
import uuid, asyncio

app = Flask(__name__)
app.config["DEBUG"] = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="jagoinstitute",
    password="sman60jakarta",
    hostname="jagoinstitute.mysql.pythonanywhere-services.com",
    databasename="jagoinstitute$default",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class AiChat(db.Model):
    __tablename__ = "aichat"
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.String(100), nullable=False, unique=True)
    chat = db.Column(db.String(4096))
    answer = db.Column(db.String(4096))

    def __repr__(self):
        return f"<{self.chat_id}>"

@app.route('/')
def hello_world():
    return 'Hello from Jago Institute!'

async def bard_chat(chat="",ai_id=""):
    token = 'YQhG5Ny6c_JujlOixF1eAMRM_6qrmMPGmGHxYJOd6RR7ytEoVLpwdPYjBEjc1qC1H2p6QQ.'
    result = Bard(token).get_answer(chat)['content']
    save_db = AiChat(chat=chat,
                        answer=result,
                        chat_id=ai_id
    )
    db.session.add(save_db)
    db.session.commit()

@app.route('/async/bard', methods=["POST","GET"])
async def async_bard():
    params = request.args
    ai_id = params.get('ai_id') if 'ai_id' in params and params.get('ai_id') else str(uuid.uuid4().hex)[:10]
    chat = params.get('chat') if 'chat' in params and params.get('chat') else ''

    # async process
    task_ai = asyncio.create_task(bard_chat(chat=chat, ai_id=ai_id))
    await task_ai

    return ai_id

@app.route('/bard', methods=["POST","GET"])
def get_ai():
    params = request.args
    ai_id = params.get('id') if 'id' in params and params.get('id') else ''

    # query db
    data = AiChat.query.filter(AiChat.chat_id == ai_id).first()
    
    result = ''
    if data:
        result = str(data.answer)

    return result

