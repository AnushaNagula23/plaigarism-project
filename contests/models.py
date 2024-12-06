import mongoengine as me
from datetime import datetime
# import constants  # Assuming constants are defined in your Django app

# Embedded Document for 'Window' field
class Window(me.EmbeddedDocument):
    start = me.DateTimeField(required=True)
    end = me.DateTimeField(required=True)

# Embedded Document for 'Participation' field
class Participation(me.EmbeddedDocument):
    userId = me.ReferenceField('User', required=True)  # Assuming 'User' is another model
    startTime = me.DateTimeField(required=True)
    endTime = me.DateTimeField()
    isStudent = me.BooleanField(required=True, default=True)

# Embedded Document for 'AllowedUser' field
class AllowedUser(me.EmbeddedDocument):
    userId = me.ReferenceField('User', required=True)
    role = me.StringField(required=True)

# Embedded Document for 'SignUp' field
class SignUp(me.EmbeddedDocument):
    userId = me.ReferenceField('User', required=True)
    signedUpTime = me.DateTimeField(required=True)

# Main Contest Document
class Contests(me.Document):
    slug = me.StringField(required=True, unique=True, trim=True)
    title = me.StringField(required=True, trim=True)
    description = me.StringField(required=True, trim=True)
    #penalty = me.IntField()

    # # Array of problem slugs
    problems = me.ListField(me.StringField(), required=True)
    meta = {
        'collection': 'contests', 
        'dynamic': True  # Allows MongoEngine to store any extra fields
    }

    # window = me.EmbeddedDocumentField(Window)
    # duration = me.IntField()  # minutes
    # signUpEnd = me.DateTimeField(default=None)

    # isAvailableForPractice = me.BooleanField(default=False)
    # hideLeaderboard = me.BooleanField(default=False)
    # practiceDuration = me.IntField()  # in days

    # participations = me.ListField(me.EmbeddedDocumentField(Participation), default=[])
    # allowedUsers = me.ListField(me.EmbeddedDocumentField(AllowedUser), default=[])
    # signUps = me.ListField(me.EmbeddedDocumentField(SignUp), default=[])
    
    # contestType = me.StringField(required=True)
    # proctoringEnabled = me.BooleanField(default=True)
    # shuffleProblems = me.BooleanField(default=False)
    # batchIds = me.ListField(me.IntField(), default=[])
    # moderators = me.ListField(me.ReferenceField('User'))  

    # specialUsers = me.ListField(me.ReferenceField('User'), default=[])
    # isZenithBatchContest = me.BooleanField(default=False)

    # createdBy = me.ReferenceField('User', required=True)
    # modifiedBy = me.ReferenceField('User', required=True)

    # meta = {
    #     'indexes': ['slug', 'title'],  # Optional indexes for faster querying
    #     'ordering': ['-createdAt']  # Optional ordering for your queries
    # }
    

    def __str__(self):
        return self.title

    # Timestamp fields
    createdAt = me.DateTimeField(default=datetime.utcnow)
    modifiedAt = me.DateTimeField(default=datetime.utcnow)

