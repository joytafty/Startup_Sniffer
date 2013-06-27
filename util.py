from sqlalchemy import create_engine, MetaData, Table, func
from sqlalchemy.orm import mapper, sessionmaker

import os
import json
import re
import time
import random
import urllib2
from datetime import datetime

import config
import socialmedia

categories = ['mobile', 'web', 'advertising', 'ecommerce', 'games_video', \
            'software', 'search']

class CBCompany(object):
    pass

class CBCompanyInfo(object):
    pass

class CBPeople(object):
    pass

class CBCompanyPeople(object):
    pass

class CBCompetitor(object):
    pass

class CBFinancial(object):
    pass

class CBExit(object):
    pass

class CBFunding(object):
    pass

class ALCompany(object):
    pass

class ALPeople(object):
    pass

class StartupInfo(object):
    pass

def load_session():
    """Connectiong to exisitng database and return session
    """
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    metadata = MetaData(engine)

    cb_companies = Table('cb_companies', metadata, autoload=True)
    mapper(CBCompany, cb_companies)
    
    cb_exits = Table('cb_exits', metadata, autoload=True)
    mapper(CBExit, cb_exits)

    cb_competitors = Table('cb_competitors', metadata, autoload=True)
    mapper(CBCompetitor, cb_competitors)

    cb_company_people = Table('cb_company_people', metadata, autoload=True)
    mapper(CBCompanyPeople, cb_company_people)

    al_companies = Table('al_companies', metadata, autoload=True)
    mapper(ALCompany, al_companies)

    startup_info = Table('startup_info', metadata, autoload=True)
    mapper(StartupInfo, startup_info)

    Session = sessionmaker(bind=engine)
    session = Session()
    
    return session

def exited_competitors_count(crunch_id, session):
    """Return the number of successful competitors of crunch_id
    """
    return session.query(CBCompetitor, CBExit).filter(
            CBCompetitor.company==crunch_id).filter(
            CBCompetitor.competitor==CBExit.company).count()

def founded_company_count(crunch_id, session):
    """Return the number of companies founder created
    """
    count = 0
    records = session.query(CBCompanyPeople).filter(
            CBCompanyPeople.company==crunch_id).all()
    
    for record in records:
        title = record.title
        if ("Founder" in title) or ("founder" in title) or ("owner" in title) or \
            ("Owner" in title) or ("Founding" in title) or ("founding" in title):
            pid = record.people
            rows = session.query(CBCompanyPeople).filter(
                    CBCompanyPeople.people==pid).all()
            for row in rows:
                ptitle = row.title
                if ("Founder" in ptitle) or ("founder" in ptitle) or \
                    ("owner" in ptitle) or ("Owner" in ptitle) or \
                    ("Founding" in ptitle) or ("founding" in ptitle):
                    count += 1
    return count

def founded_company_exit_count(crunch_id, session):
    """Return the number of exited companies founder created
    """
    count = 0
    records = session.query(CBCompanyPeople).filter(
            CBCompanyPeople.company==crunch_id).all()
    
    for record in records:
        title = record.title
        if ("Founder" in title) or ("founder" in title) or ("owner" in title) or \
            ("Owner" in title) or ("Founding" in title) or ("founding" in title):
            pid = record.people
            rows = session.query(CBCompanyPeople).filter(
                    CBCompanyPeople.people==pid).all()
            for row in rows:
                ptitle = row.title
                if ("Founder" in ptitle) or ("founder" in ptitle) or \
                    ("owner" in ptitle) or ("Owner" in ptitle) or \
                    ("Founding" in ptitle) or ("founding" in ptitle):
                    count += session.query(CBExit).filter(
                            CBExit.company==row.company).count()
    return count

def generate_training_data(session):
    """ Get training companies data in categoeis
    """
    companies = session.query(CBCompany).filter(
            CBCompany.category.in_(categories)).all()
    
    fh = open('data/training.csv', "w")
    fh.write("crunch_id,milestone_num,competitor_num,office_num,product_num," + \
             "service_num,founding_round_num,total_money_raised,acquisition_num," + \
             "investment_num,vc_num,num_exited_competitor,company_count," + \
             "exited_company_count,success\n")
    
    for company in companies:
        crunch_id = company.crunch_id
        exit_record = session.query(CBExit).filter(
                CBExit.company==crunch_id).first()
        if exit_record is None: # Negative instances
            if company.founded_year is not None and company.founded_year<2009:
                success = 0
                amount = None
            else:
                continue
        else: # positive instances
            success = 1
            amount = exit_record.valuation

        num_exited_competitor = exited_competitors_count(
                company.crunch_id, session)
        
        company_count = founded_company_count(company.crunch_id, session)

        exited_company_count = founded_company_exit_count(
                company.crunch_id, session)

        total_money_raised = float(company.total_money_raised) / 10000000.0
        success = 1 if company.success==1 else 0
        fh.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%d,%d,%d,%s\n" % \
                  (company.crunch_id, company.milestone_num, \
                   company.competitor_num, company.office_num, \
                   company.product_num, company.service_num, \
                   company.founding_round_num, total_money_raised, \
                   company.acquisition_num, company.investment_num, \
                   company.vc_num, num_exited_competitor, company_count, \
                   exited_company_count, success))
    fh.close()

def generate_testing_data(session):
    """ Get testing companies data in categoeis
    """
    companies = session.query(CBCompany).filter(
            CBCompany.category.in_(categories)).filter(
            CBCompany.founded_year>=2007).all()
    
    fh = open('data/predict_com.csv', "w")
    fh.write("crunch_id,milestone_num,competitor_num,office_num,product_num,service_num," + \
             "founding_round_num,total_money_raised,acquisition_num,investment_num,vc_num," + \
             "num_exited_competitor,company_count,exited_company_count\n")

    for company in companies:
        crunch_id = company.crunch_id
        
        num = session.query(CBExit).filter(CBExit.company==crunch_id).count()
        if num > 0:
            continue

        num_exited_competitor = exited_competitors_count(
                company.crunch_id, session)
        
        company_count = founded_company_count(company.crunch_id, session)

        exited_company_count = founded_company_exit_count(
                company.crunch_id, session)

        total_money_raised = float(company.total_money_raised) / 10000000.0
        
        fh.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%d,%d,%d\n" % \
                  (company.crunch_id, company.milestone_num, \
                   company.competitor_num, company.office_num, \
                   company.product_num, company.service_num, \
                   company.founding_round_num, total_money_raised, \
                   company.acquisition_num, company.investment_num, \
                   company.vc_num, num_exited_competitor, \
                   company_count, exited_company_count))
    fh.close()

def update_startup_info(session):
    """ Insert tracking information for each startup for today into database
    """
    startups = session.query(CBCompany, ALCompany).filter(
            CBCompany.name==ALCompany.name).filter(
            CBCompany.twitter is not None).filter(
            func.char_length(CBCompany.twitter)>0).all()
    
    for startup in startups:
        al_id = startup.ALCompany.angellist_id
        print al_id
        
        count = session.query(StartupInfo).filter(StartupInfo.al_id==al_id).filter(
                    StartupInfo.info_date==datetime.today().date()).count()
        if count > 0:
            continue
        else:
            record = StartupInfo()
        
        al_url = "https://api.angel.co/1/startups/%d?access_token=%s" % \
            (al_id, config.ANGELLIST_TOKEN)
        resp = urllib2.urlopen(al_url)
        profile = json.loads(resp.read())
        
        record.info_date = datetime.today().date()
        record.al_id = al_id
        record.al_follower = profile['follower_count']
        record.al_quality = profile['quality']
        
        twitter_profile = socialmedia.twitter_user_show(startup.CBCompany.twitter)
        record.twitter_follower = twitter_profile['followers_count']
        
        record.bitly_click = socialmedia.bitly_click_count(
                startup.ALCompany.bitly_hash)
        
        session.add(record)
        session.commit()

def update_bity_hash(session):
    """ Save bitly.com url hash for each startup company
    """
    al_startups = session.query(ALCompany).filter(
            ALCompany.company_url is not None).all()
    for startup in al_startups:
        if startup.bitly_hash is not None:
            continue 

        bitly_hash = socialmedia.get_bitly_hash(startup.company_url)
        
        if bitly_hash is not None:
            startup.bitly_hash = bitly_hash
            session.add(startup)
        else:
            print "%s, %s hash is none" % (startup.name, startup.id)

    session.commit()

def main():
    session = load_session()
    
    #generate_training_data(session)
    
    #generate_testing_data(session)
    
    session.close()

if __name__ == "__main__":
    main()

