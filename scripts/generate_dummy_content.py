# -*- coding: utf-8 -*-

# This script is intended to be used in a test environment, to generate enough
# content so the feature of split sitemaps can be tested

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.User import system
from Acquisition import aq_parent
from Testing.makerequest import makerequest
from zope.component.hooks import setSite
from zope.globalrequest import setRequest
from plone import api
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFCore.interfaces._content import IContentish
import random
import sys
import transaction

NUMBER_OF_ITEMS = int(sys.argv[-1])

LIPSUM = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec mauris nisi, feugiat nec tincidunt a, ornare nec risus. Morbi fringilla quam at commodo ultricies. Etiam vulputate ex sit amet ante ultricies interdum. Ut lacinia mattis sodales. Morbi ultrices sem et leo gravida, eget pellentesque dui luctus. Vivamus ornare luctus lectus vitae rhoncus. Etiam porta, ex id convallis dapibus, risus dui finibus augue, vel auctor sem metus at orci. Praesent vestibulum purus a turpis convallis consequat. Suspendisse commodo felis vitae tincidunt lobortis.

Nullam non libero ac justo euismod viverra. Nullam vitae varius tellus. Nunc mattis hendrerit felis, non ornare dolor volutpat quis. Curabitur lobortis eleifend metus, consequat ullamcorper sapien egestas ac. Vestibulum risus turpis, tempus id ullamcorper ac, dictum sagittis velit. Nam ornare libero id tellus facilisis, nec lacinia dui venenatis. Sed molestie ligula dictum felis blandit, non consectetur nisl convallis.

Nunc ultrices massa pellentesque justo pulvinar viverra a eu lectus. In non volutpat urna. Nulla cursus massa sapien, a ultrices tellus suscipit sit amet. In facilisis rhoncus leo, nec molestie lacus porta in. Nullam vestibulum efficitur massa et semper. Nunc vitae nibh sagittis quam mattis gravida ac ornare lorem. Aliquam ac augue vulputate, faucibus ante sed, condimentum est. Quisque feugiat tellus sit amet erat fringilla suscipit.

Ut rutrum elit vel odio facilisis mattis. Morbi sollicitudin vulputate tortor sit amet ullamcorper. Morbi ultricies nisi vitae accumsan facilisis. Sed id consectetur ex. Aliquam molestie ante eu tristique auctor. Sed sagittis lectus id erat facilisis pharetra. Pellentesque sagittis ultricies mollis. Nulla malesuada hendrerit sem eget rhoncus. Quisque quis sem gravida ligula luctus euismod eget eget lectus. Sed scelerisque massa quis arcu convallis egestas. Sed venenatis lectus mauris, vitae bibendum erat volutpat vitae. Quisque efficitur, lectus a facilisis fermentum, velit orci condimentum purus, sed interdum neque augue sed erat. Aliquam faucibus auctor ipsum id tincidunt. Morbi volutpat velit ac arcu dignissim scelerisque. Nam id ipsum erat. Sed ut fermentum sem.

Mauris tristique, ligula a rutrum ultrices, risus lectus interdum orci, laoreet laoreet sem ligula quis eros. Aliquam vel magna mattis magna malesuada scelerisque. Proin ac ultricies diam. Nulla feugiat, nisi ultrices porttitor scelerisque, nibh elit ultrices dui, at varius libero orci quis lectus. Etiam luctus molestie nulla, vitae ullamcorper justo rhoncus non. In ultricies dui in libero rhoncus, quis tempor odio consequat. Curabitur ut malesuada lorem. In a faucibus urna.
"""

app = makerequest(app)
newSecurityManager(None, system)

MAX_DEPTH = 10

for id in app:
    portal = app.get(id)
    if IPloneSiteRoot.providedBy(portal):
        setSite(portal)
        portal.REQUEST["PARENTS"] = [portal]
        portal.REQUEST.setVirtualRoot("/")
        setRequest(portal.REQUEST)
        portal.REQUEST["SERVER_NAME"] = "www.mysite.com"
        portal.REQUEST["SERVER_URL"] = "https://www.mysite.com"

        context = portal
        idx = 0
        while idx < NUMBER_OF_ITEMS:
            # We will be randomly either creating content, going up or going
            # inside a folder
            ct_to_create = [
                'Folder',
                'Document',
            ]
            actions = list()
            if IPloneSiteRoot.providedBy(context):
                items = context.listFolderContents()
                if len(items) < 8:
                    actions.append('create')
                    ct_to_create = [
                        'Folder',
                    ]
            if not IPloneSiteRoot.providedBy(context):
                actions.append('create')
                actions.append('create')
                actions.append('create')
                actions.append('create')
                actions.append('create')  # Increase chances of creating content
                actions.append('up')
            if len(context.getPhysicalPath()) - 2 < MAX_DEPTH:
                folders = context.listFolderContents(
                    contentFilter={'portal_type': ['Folder']}
                )
                if folders:
                    random_folder = random.choice(folders)
                    if random_folder.id != "Members":
                        actions.append(random_folder)

            if actions:
                action = random.choice(actions)

                if action == 'up':
                    context = aq_parent(context)
                elif action == 'create':
                    pt = random.choice(ct_to_create)
                    try:
                        new_obj = api.content.create(
                            container=context,
                            type=pt,
                            title=random.choice(LIPSUM.split())
                        )
                    except:
                        continue
                    idx += 1
                    if idx % 500 == 0:
                        print "Created %s items." % idx
                else:
                    context = action


transaction.commit()
