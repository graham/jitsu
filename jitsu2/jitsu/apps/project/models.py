import jitsu.db.row
import jitsu.modules.session

class Project(jitsu.db.Row):
    manager       = jitsu.db.ForeignKey(jitsu.modules.session.User)
    members       = jitsu.db.Many(jitsu.modules.session.User)
    hour_value    = jitsu.db.IntegerField()
    
class Milestone(jitsu.db.Row):
    project       = jitsu.db.ForeignKey(Project)
    slug          = jitsu.db.CharField(128)
    version       = jitsu.db.IntegerField()
    minor         = jitsu.db.IntegerField()

class Sprint(jitsu.db.Row):
    milestone     = jitsu.db.ForeignKey(Milestone)
    name          = jitsu.db.CharField(128)

class Feature(jitsu.db.Row):
    project       = jitsu.db.ForeignKey(Project)
    milestone     = jitsu.db.ForeignKey(Milestone)
    sprint        = jitsu.db.ForeignKey(Sprint)
    slug          = jitsu.db.CharField(128)
    description   = jitsu.db.TextField()
    hour_estimate = jitsu.db.IntegerField()
    
class Bug(jistu.db.Row):
    project       = jitsu.db.ForeignKey(Project)
    slug          = jitsu.db.CharField(128)
    description   = jitsu.db.TextField()

class Test(jitsu.db.Row):
    project       = jitsu.db.ForeignKey(Project)
    feature       = jitsu.db.ForeignKey()
