# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import asyncio
import json

from application import BOT
from application.home import blueprint
from flask import render_template, redirect, url_for, request, Response, jsonify
from flask_login import login_required, current_user
from application import login_manager
from jinja2 import TemplateNotFound

@blueprint.route('/index')
@login_required
def index():
    return render_template('index.html', segment='index')

@blueprint.route('/bot-data', methods=['POST'])
@login_required
def bot_data():
    BOT.trade.update_assets()
    return jsonify(BOT.to_json())


@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:
        if not template.endswith( '.html' ):
            template += '.html'

        # Detect the current page
        segment = get_segment( request )

        # Serve the file (if exists) from application/templates/FILE.html
        return render_template( template, segment=segment )

    except TemplateNotFound:
        return render_template('page-404.html'), 404
    
    except:
        return render_template('page-500.html'), 500

# Helper - Extract current page name from request 
def get_segment( request ): 

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment    

    except:
        return None  
