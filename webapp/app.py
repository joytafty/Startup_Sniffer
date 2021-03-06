from flask import Flask, session, flash, request
from flask import redirect, url_for, render_template
from flask.ext.sqlalchemy import SQLAlchemy
import MySQLdb as mdb
from pandas import DataFrame
# import pyodbc
import pandas.io.sql as psql

from models import *
import os
import re
import socket
from flask_oauth import OAuth
import pandas as pd
import numpy as np
import pickle
import json
from datetime import date, timedelta
import time

import sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_STATIC = os.path.join(APP_ROOT, 'static')

app = Flask(__name__)
app.config.from_object('config')

con = mdb.connect('localhost', 'joyinsight', 'san00k', 'insightdata')
with con:     
    d = con.cursor()
    query = """
        SELECT DISTINCT * FROM prob_acquire as t1
        JOIN startups_seed_fund as t2 ON t1.name = t2.name
        ORDER BY t1.successidx DESC

        """
    df = psql.read_frame(query, con)
    df = df.T.drop_duplicates(take_last=True).T
    d.close()

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

# @app.route('/slides')
# def slides():
#     return render_template("slides.html")

# @app.route('/slideshare')
# def slideshare():
#     return render_template("slideshare.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def not_found(error):
    return render_template('500.html'), 500

@app.route('/board')
def board():
    # Get latest metric data

    # records = db.session.query(StartupInfo, ALCompany).filter(
    #         StartupInfo.al_id==ALCompany.angellist_id).filter(
    #         StartupInfo.info_date==date.today()).all()
    
    # if len(records) == 0:
    #     records = db.session.query(StartupInfo, ALCompany).filter(
    #         StartupInfo.al_id==ALCompany.angellist_id).filter(
    #         StartupInfo.info_date==(date.today()-timedelta(1))).all()
    
    # # Get past metric data to compute trend
    # past_records = db.session.query(StartupInfo, ALCompany).filter(
    #         StartupInfo.al_id==ALCompany.angellist_id).filter(
    #         StartupInfo.info_date==(date.today()-timedelta(7))).all()

    # # Find maximum number of each tracking metric
    # data = {"angellist":0, "twitter":0, 'bitly':0}
    # for record in records:
    #     al_follower = record.StartupInfo.al_follower
    #     twitter = record.StartupInfo.twitter_follower
    #     bitly = record.StartupInfo.bitly_click
        
    #     if al_follower > data['angellist']:
    #         data['angellist'] = al_follower
    #     if twitter > data['twitter']:
    #         data['twitter'] = twitter
    #     if bitly > data['bitly']:
    #         data['bitly'] = bitly


    # Normalize latest data to rank startups and compute trend at the
    # same time 
    records = df.sort(column='successidx',ascending=True)[:20]
    ranked_list = {}
    for record in records:        
    # trend_list = {}
        name = df.name
        success_prob = df.successidx
        status = df.status
        market = df.category_code
        valuation = df.acquisition_price
        location = df.locations

        ranked_list['name'] = [name, success_prob, status, market, valuation, location]
            # rank
#         nor_al_follower = (al_follower / float(data['angellist'])) * 100.0
#         nor_al_quality = al_quality * 10.0
#         nor_bitly = (bitly / float(data['bitly'])) * 100.0
#         nor_twitter = (twitter / float(data['twitter'])) * 100.0
#         score = 0.25 * nor_al_follower + 0.25 * nor_al_quality + \
#                 0.25 * nor_bitly + 0.25 * nor_twitter
        
        # ranked_list[al_id] = {}
        # ranked_list[al_id]['score'] = success_prob
        # ranked_list[al_id]['data'] = [name, success_prob, status, market, valuation, location]

#         # trend
#         al_follow_trend = (al_follower - past_data[al_id][0]) / 7
#         al_quality_trend = (al_quality - past_data[al_id][1]) /7
#         twitter_trend = (twitter - past_data[al_id][2]) / 7
#         bitly_trend = (bitly - past_data[al_id][3]) / 7
        # trend_list[al_id] = {}
        # trend_list[al_id]['score'] = al_follow_trend + al_quality_trend + \
        #                              twitter_trend + bitly_trend
        # trend_list[al_id]['data'] = [name, al_quality, al_follower, twitter, bitly, img]

    # ranked_list = sorted(ranked_list.items(), key=lambda x: x[1]['score'], 
    #         reverse=True)[0:20]
    # trend_list = sorted(trend_list.items(), key=lambda x: x[1]['score'], 
    #         reverse=True)[0:20]
    print type(location)

    return render_template("board.html", ranked_list=ranked_list, 
        name=name, score=success_prob, 
        status=status, market=market, valuation=valuation, location=location,
        inds=range(len(name)))
    
    # return render_template("board.html", ranked_list=ranked_list, 
    #         trend_list=trend_list)

@app.route('/all')
def all():
#     # Get latest metric data
#     records = db.session.query(StartupInfo, ALCompany).filter(
#             StartupInfo.al_id==ALCompany.angellist_id).filter(
#             StartupInfo.info_date==date.today()).all()
    
#     if len(records) == 0:
#         records = db.session.query(StartupInfo, ALCompany).filter(
#             StartupInfo.al_id==ALCompany.angellist_id).filter(
#             StartupInfo.info_date==(date.today()-timedelta(1))).all()
    
#     # Get past metric data to compute trend
#     past_records = db.session.query(StartupInfo, ALCompany).filter(
#             StartupInfo.al_id==ALCompany.angellist_id).filter(
#             StartupInfo.info_date==(date.today()-timedelta(7))).all()

#     # Find maximum number of each tracking metric
#     data = {"angellist":0, "twitter":0, 'bitly':0}
#     for record in records:
#         al_follower = record.StartupInfo.al_follower
#         twitter = record.StartupInfo.twitter_follower
#         bitly = record.StartupInfo.bitly_click
        
#         if al_follower > data['angellist']:
#             data['angellist'] = al_follower
#         if twitter > data['twitter']:
#             data['twitter'] = twitter
#         if bitly > data['bitly']:
#             data['bitly'] = bitly
    
#     # Cache past data
#     past_data = {}
#     for record in past_records:
#         al_follower = record.StartupInfo.al_follower
#         al_quality = record.StartupInfo.al_quality
#         twitter = record.StartupInfo.twitter_follower
#         bitly = record.StartupInfo.bitly_click
#         al_id = record.StartupInfo.al_id
#         past_data[al_id] = [al_follower, al_quality, twitter, bitly]

#     # Normalize latest data to rank startups and compute trend at the
#     # same time 
#     ranked_list = {}
#     trend_list = {}
#     for record in records:
#         al_follower = record.StartupInfo.al_follower
#         al_quality = record.StartupInfo.al_quality
#         twitter = record.StartupInfo.twitter_follower
#         bitly = record.StartupInfo.bitly_click
#         al_id = record.StartupInfo.al_id
#         name = record.ALCompany.name
#         img = record.ALCompany.logo_url

#         # rank
#         nor_al_follower = (al_follower / float(data['angellist'])) * 100.0
#         nor_al_quality = al_quality * 10.0
#         nor_bitly = (bitly / float(data['bitly'])) * 100.0
#         nor_twitter = (twitter / float(data['twitter'])) * 100.0
#         score = 0.25 * nor_al_follower + 0.25 * nor_al_quality + \
#                 0.25 * nor_bitly + 0.25 * nor_twitter
        
#         ranked_list[al_id] = {}
#         ranked_list[al_id]['score'] = score
#         ranked_list[al_id]['data'] = [name, al_quality, al_follower, twitter, bitly, img]

#         # trend
#         al_follow_trend = (al_follower - past_data[al_id][0]) / 7
#         al_quality_trend = (al_quality - past_data[al_id][1]) /7
#         twitter_trend = (twitter - past_data[al_id][2]) / 7
#         bitly_trend = (bitly - past_data[al_id][3]) / 7
#         trend_list[al_id] = {}
#         trend_list[al_id]['score'] = al_follow_trend + al_quality_trend + \
#                                      twitter_trend + bitly_trend
#         trend_list[al_id]['data'] = [name, al_quality, al_follower, twitter, bitly, img]

#     ranked_list = sorted(ranked_list.items(), key=lambda x: x[1]['score'], 
#             reverse=True)
#     trend_list = sorted(trend_list.items(), key=lambda x: x[1]['score'], 
#             reverse=True)
    # return render_template("all.html", ranked_list='', trend_list='ranked_list')    
    return render_template("about.html")


# @app.route('/startup')
# @app.route('/startup/<int:al_id>')
# def startup(al_id):
#     al_com = db.session.query(ALCompany).filter(
#             ALCompany.angellist_id==al_id).first()

#     start_date = date.today()-timedelta(15)
#     records = db.session.query(StartupInfo).filter(
#             StartupInfo.al_id==al_id).filter(
#             StartupInfo.info_date>=start_date).order_by(
#                     StartupInfo.info_date).all()

#     twitter_data = []
#     al_follower_data = []
#     al_quality_data = []
#     bitly_data = []

#     for record in records:
#         ts = int(round(float(record.info_date.strftime("%s.%f")), 3)) * 1000
#         twitter_data.append([ts, record.twitter_follower])
#         al_follower_data.append([ts, record.al_follower])
#         al_quality_data.append([ts, record.al_quality])
#         bitly_data.append([ts, record.bitly_click])

#     data = [
#              {"key": "Twitter follower", "values": twitter_data},
#              {"key": "Angellist follower", "values": al_follower_data},
#              {"key": "Angellist quality", "values": al_quality_data},
#              {"key": "Bitly click", "values": bitly_data},
#     ];
    
#     return render_template("startup.html", data=data, al_com=al_com)
    
@app.route('/predict')
def predict():
    # records = db.session.query(al_companies).filter(
    #         ALCompany.logo_url != None).limit(22)
    df = pd.read_csv(os.path.join(APP_STATIC, 'predict_com.csv'), header=0, index_col=0)
    comp_json = json.dumps(["%s (%s)" % (df.ix[cid]['name'], cid) for cid in df.index.values])
    fp = os.path.join(APP_STATIC, 'com.json')
    json_data = open(fp).read()
    comp_json = json.loads(json_data)
    return render_template("predict.html", comp_json=comp_json)

@app.route('/analyze/', methods=['POST'])
def analyze():
    fp = os.path.join(APP_STATIC, 'com.json')
    json_data = open(fp).read()
    comp_json = json.loads(json_data)

#     records = db.session.query(al_companies).filter(
#             ALCompany.logo_url != None).limit(22)

#     crunch_id = request.form.get('crunch-id', None)
#     if (crunch_id is None) or (len(crunch_id.strip())==0):
#         flash('Please input valid startup name')
#         return render_template('predict.html', comp_json=comp_json, records=records)
    
#     matobj = re.search("\((.*)\)", crunch_id)
#     if matobj:
#         crunch_id = matobj.group(1)
#     else:
#         crunch_id = None
    
#     if crunch_id is None:
#         flash('Sorry, the input company is not in our database')
#         return render_template('predict.html', comp_json=comp_json, records=records)

#     model = pickle.load(open(os.path.join(APP_STATIC, 'rf.model')))
    
#     #df = pd.read_csv(os.path.join(APP_STATIC, 'predict_com.csv'), header=0, index_col=0)
#     #del df['name']
    
#     record = db.session.query(precompanies).filter(
#             PreCompany.crunch_id == crunch_id).first()

#     if record is None:
#         flash('Sorry, the input company is not in our database')
#         return render_template('predict.html', comp_json=comp_json, records=records)

#     #row = np.array(df.ix[crunch_id])
#     row = np.array([record.milestone_num, record.competitor_num, 
#                     record.office_num, record.product_num, 
#                     record.service_num, record.founding_round_num, 
#                     record.total_money_raised, record.acquisition_num, 
#                     record.investment_num, record.vc_num, 
#                     record.num_exited_competitor, record.company_count, 
#                     record.exited_company_count])
    
#     prob = model.predict_proba(row)
#     prob_value = prob[0][1]
#     prob = "%.2f%%" % (prob[0][1]*100.0)
    
#     if prob_value<=0.3:
#         valuation = "Don't bother"
#     else:
#         regression_model = pickle.load(open(os.path.join(APP_STATIC, 'rf_regression.model')))
#         valuation = regression_model.predict(row)[0]
#         valuation = "$ %.2f Million" % valuation

#     record = db.session.query(cb_companies).filter(
#             CBCompany.crunch_id==crunch_id).first()
    
#     com_record = db.session.query(cb_companies).filter(
#             CBCompany.crunch_id==crunch_id).first()
#     return render_template("analyze.html", prob=prob, \
#             company=record, comp_json=comp_json, com_record=com_record, valuation=valuation)

# @app.route('/job')
# def job():
#     return render_template("job.html")

# @app.route('/recommend')
# def recommend():
#     try:
#         token = session['user_oauth_token']
#     except KeyError:
#         token = None

#     if token == None:
#         return redirect(url_for('job.login'))

#     profile_req_url = 'http://api.linkedin.com/v1/people/~:' + \
#         '(id,first-name,last-name,industry,interests,skills,educations,' + \
#         'courses,three-current-positions)?format=json'
#     resp = linkedin.get(profile_req_url)
    
#     if resp.status == 200:
#         profile = resp.data

#     return render_template('recommend.html', Profile=profile)

if __name__ == "__main__":
    # if socket.gethostbyname(socket.gethostname()).startswith('192'):
    #     port = 5000
    # else:
    #     port = 80

    # app.run(host='0.0.0.0', port=port, debug=True, threaded=True)
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)

