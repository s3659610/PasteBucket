import time

import boto3
from flask import Flask, render_template, redirect, request, jsonify, session
import LoginFunctions, PostFunctions
import random, string
application = Flask(__name__)

application.secret_key = 'cloudComputingIsFun'

"""""""""""""""
  404 ROUTE 
"""""""""""""""
@application.errorhandler(404)
def page_not_found(e):
    if 'username' in session:
        return render_template('404.html', user=session['username'].upper()),404
    else:
        return render_template('404.html'),404


"""""""""""""""
STANDARD ROUTES 
"""""""""""""""
@application.route('/global')
def global_posts():

    globalPosts = PostFunctions.getGlobal()

    if 'username' in session:
        return render_template('global.html', user=session['username'].upper(), globalPosts=globalPosts, globalPostsLen=len(globalPosts))
    else:
        return render_template('global.html', globalPosts=globalPosts, globalPostsLen=len(globalPosts))

@application.route('/')
def land_page():
    trending = PostFunctions.getTrendingPosts()
    recent = PostFunctions.getRecentPosts()
    # if user is login in change nav to show profile "li tag" instead of sign in and sign up
    # check if session varible set if they are change nav as aforementioned
    # else display standard template
    if 'username' in session:
        return render_template('index.html', user=session['username'].upper(), trending=trending, trendingLen=len(trending), recent=recent, recentLen=len(recent))
    else:
        return render_template('index.html', trending=trending, trendingLen=len(trending), recent=recent, recentLen=len(recent))

@application.route('/signin', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # perhaps some security parsing?
        print(username)

        if (LoginFunctions.sign_in(username, password) != None):
            user = LoginFunctions.sign_in(username, password)
            session['username'] = username
            return redirect("/")
        else:
            error = "Wrong Username and/or Password!"
            if 'username' in session:
                return render_template('signin.html', error=error, user=session['username'].upper())
            else:
                return render_template('signin.html', error=error)

    else:
        if 'username' in session:
            return render_template('signin.html', user=session['username'].upper())
        else:
            return render_template('signin.html')


@application.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # perhaps some security parsing?
        ## 1. Check if email exists
        if (LoginFunctions.check_username_exists(username)):
            error = "Username Already Exists"
            if 'username' in session:
                return render_template('signup.html', error=error, user=session['username'].upper())
            else:
                return render_template('signup.html', error=error)
        else:
            # create user
            if(LoginFunctions.sign_up(username, password)):
                print("user created")
                # redirect to user-page
                return redirect("/signin")
            else:
                error = "Error in creating user"
                if 'username' in session:
                    return render_template('signup.html', error=error, user=session['username'].upper())
                else:
                    return render_template('signup.html', error=error)
    else:
        if 'username' in session:
            return render_template('signup.html', user=session['username'].upper())
        else:
            return render_template('signup.html')

@application.route('/aboutus')
def aboutus():
    if 'username' in session:
        return render_template('aboutus.html', user=session['username'].upper())
    else:
        return render_template('aboutus.html')

"""""""""""""""""""""
  DASHBOARD ROUTES 
"""""""""""""""""""""

@application.route('/dashboard')
def dashboard():
    trending = PostFunctions.getTrendingPosts()
    recent = PostFunctions.getRecentPosts()
    if 'username' in session:
        # array of posts
        user_posts = PostFunctions.getUserPosts(session['username'])
        number_of_posts = len(user_posts)
        return render_template('dashboard.html', user=session['username'].upper(),
                               posts=user_posts, len=number_of_posts,
                               trending=trending, trendingLen=len(trending),
                               recent=recent, recentLen=len(recent))
    else:
        return redirect('/')


@application.route('/logout')
def logout():
    session.pop('username')
    return redirect("/")

"""""""""""""""
  POST ROUTES 
"""""""""""""""

@application.route('/post/<string:post_id>')
def post(post_id):
    """
        FLOW:
        Update view in post item in database

    """
    trending = PostFunctions.getTrendingPosts()
    recent = PostFunctions.getRecentPosts()
    # if post doesnt exist revert to 404

    if 'username' in session:
        postObject = PostFunctions.getPasteTypeText(post_id)
        # burn paste
        if((postObject['burn'] == 1) and postObject['page_views'] >= 2):
            print('here')
            # delete post from posts
            PostFunctions.burnPost(postObject['post_id'])
            return redirect("/404"), 404, {"Refresh": "1; url=/404"}


        try:
            PostFunctions.addView(post_id)
        except Exception as e:
            print(e)

        error = None
        if(postObject == False):
            error = "error in fetching post"
            return redirect("/404"), 404, {"Refresh": "1; url=/404"}


        image = None
        if(postObject['type'] == "image"):
            ## fetch image from s3 and add give to template as base64 dataurl
            fileType = postObject['fileType']
            image = PostFunctions.getImage(postObject['post_id'], fileType)


        return render_template('post.html', user=session['username'].upper(),
                               post=postObject, trending=trending,
                               trendingLen=len(trending),recent=recent, recentLen=len(recent), image=image)

    else:
        postObject = PostFunctions.getPasteTypeText(post_id)
        if((postObject['burn'] == 1) and postObject['page_views'] >= 2):
            print('here')
            # delete post from posts
            PostFunctions.burnPost(postObject['post_id'])
            return redirect("/404"), 404, {"Refresh": "1; url=/404"}

        if(postObject == False):
            error = "error in fetching post"
            return redirect("/404"), 404, {"Refresh": "1; url=/404"}


        image = None
        if(postObject['type'] == "image"):
            ## fetch image from s3 and add give to template as base64 dataurl
            fileType = postObject['fileType']
            image = PostFunctions.getImage(postObject['post_id'], fileType)

        try:
            PostFunctions.addView(post_id)
        except Exception as e:
            print(e)


        return render_template('post.html', post=postObject, trending=trending, trendingLen=len(trending),recent=recent, recentLen=len(recent), image=image)

@application.route('/pastetext', methods=['GET', 'POST'])
def pasteText():
    # create post id
    # collect all data
    # add data
    # if someone is sign in it gets added to their posts
    # type of post
    type = "text"
    # post body
    post = request.form.get('post')
    # for text type description can be the first 100 charcters
    description = post[:50]
    # views, number of people that have view post
    views = 0

    # author
    author = request.form.get('author')
    if(author == ""):
        author = "Anonymous"
    title = request.form.get('title')
    if(title == ""):
        title = "untitled"
    # hours the user wishs the post to be alive for
    ttl = request.form.get('time-to-live')
    # 10 alphanumeric random string as post id
    post_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
    # future time to delete post
    delete_time = ""
    # time post created
    time_posted = int(time.time())
    # ip address of poster
    ip_address = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)

    if (ttl != "burn"):
        burn = 0
        delete_time = int(time.time()) + int(ttl) * 60 * 60
    else:
        burn = 1


    if 'username' in session:
        user = session['username']
    else:
        # not signed in
        user = ""

    if(PostFunctions.pasteText(type, post_id, post, title, description, views, author, delete_time, burn, time_posted, ip_address, user)):
        # post success
        return redirect("/post/{}".format(post_id))
    else:
        # post failure
        error = "error in creating post"
        return render_template("index.html", error=error)


@application.route('/pasteimage', methods=['GET', 'POST'])
def pasteImage():
    image = request.files['img']
    # create post id
    # collect all data
    # add data
    # if someone is sign in it gets added to their posts
    # type of post
    type = "image"
    # post body
    # for text type description can be the first 100 charcters
    # views, number of people that have view post
    views = 0
    # author
    author = request.form.get('author')
    if(author == ""):
        author = "Anonymous"
    title = request.form.get('title')
    if(title == ""):
        title = "untitled"
    # hours the user wishs the post to be alive for
    ttl = request.form.get('time-to-live')
    # 10 alphanumeric random string as post id
    post_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
    # future time to delete post
    delete_time = ""
    # time post created
    time_posted = int(time.time())
    # ip address of poster
    ip_address = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)

    if (ttl != "burn"):
        burn = 0
        delete_time = int(time.time()) + int(ttl) * 60 * 60
    else:
        burn = 1

    if 'username' in session:
        user = session['username']
    else:
        # not signed in
        user = ""

    print(image)
    # standard fillins
    description = "image description"
    post = "image post"
    fileType  = image.filename[image.filename.index(".") + 0:image.filename.rindex(".") + 4]
    if(PostFunctions.pasteImage(type, post_id, post, title, description, views, author, delete_time, burn, time_posted, ip_address, user, image, fileType)):
        # post success
        return redirect("/post/{}".format(post_id))
    else:
        # post failure
        error = "error in creating post"
        return render_template("index.html", error=error)

if __name__ == '__main__':
    application.debug = True
    application.run()
