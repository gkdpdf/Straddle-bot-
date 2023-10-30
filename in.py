from api_helper import ShoonyaApiPy
from datetime import datetime, date, time, timedelta
import numpy as np
import time as t
import pandas as pd
import streamlit as st

# api credentials
uid = 'FA153221'
pwd = 'Gaurav@1234'
vc = 'FA153221_U'
app_key = 'bfbdeedf98be606ab079462ca74eb37e'
imei = 'abc1234'

# api object
api = ShoonyaApiPy()

st.title('Automatic Trading Algorithm using Shoonya API')
factor2 = st.text_input("Enter 2FA: ")
ret = api.login(userid=uid, password=pwd, twoFA=factor2, vendor_code=vc,
                 api_secret=app_key, imei=imei)
if factor2:
    st.write('login done for : ', ret['uname'])

    
    
    def closest(lst, K):
        
        return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))]

    def get_symbol(name,exp,typ,strike):
        return name+exp+typ+strike

    def placeOrder(symbol,buy_sell,qty):
        api.place_order(buy_or_sell=buy_sell, product_type='I',
                                exchange='NFO', tradingsymbol=symbol, 
                                quantity=qty, discloseqty=0,price_type='MKT',
                                retention='DAY', remarks='my_order_put')
        
    def get_mtm():
        ret = api.get_positions()
        mtm = 0
        pnl = 0
        day_m2m=0
        for i in ret:
            mtm += float(i['urmtom'])
            pnl += float(i['rpnl'])
            day_m2m = mtm + pnl
        st.write(f'{day_m2m} is your Daily MTM')
        
        return day_m2m

    def uni_exit() :

        while True:
            try : 
                a=api.get_positions()
                a=pd.DataFrame(a)
                ob = api.get_order_book()
                ob = pd.DataFrame(ob)
                break
            except Exception :
                st.write('uni_exit error fetching positions/orders')
                t.sleep(1)
                continue

        for i in a.itertuples():

            if int(i.netqty)<0: api.place_order(buy_or_sell='B', product_type=i.prd, exchange=i.exch, tradingsymbol=i.tsym,  quantity=abs(int(i.netqty)), discloseqty=0,price_type='MKT', price=0, trigger_price=None,
                                retention='DAY', remarks='killswitch_buy')

            if int(i.netqty)>0: api.place_order(buy_or_sell='S', product_type=i.prd, exchange=i.exch, tradingsymbol=i.tsym,  quantity=int(i.netqty), discloseqty=0,price_type='MKT', price=0, trigger_price=None,
                                retention='DAY', remarks='killswitch_sell')

    #     ob = api.get_order_book()
    #     ob = pd.DataFrame(ob)
        for i in ob.itertuples():

            if i.status == 'TRIGGER_PENDING': ret = api.cancel_order(i.norenordno)
            if i.status == 'OPEN': ret = api.cancel_order(i.norenordno) 
        
        


    all_symbols=pd.read_csv('https://api.shoonya.com/NSE_symbols.txt.zip')
    def getLTP(symbol,exch,all_symbols):
        token=str(all_symbols[all_symbols['TradingSymbol']==symbol]['Token'].values[0])
        ltp=api.get_quotes(exchange=exch, token=token)['lp']
        return ltp

    def straddle(expiry,lot):
        #rr=2
        exip=expiry
        #lot=1
        qty=lot*15

        start=time(9,50,1)
        end=time(15,5,1)
        pt1=datetime.now().time()
        while(pt1<start):
            pt1=datetime.now().time()


            
        tick='NIFTY BANK'
        q=0
        while(q<3):
            try:
                ltp=float(getLTP(tick,'NSE',all_symbols))
            except Exception as e:
                pass
            q+=1
            t.sleep(1)
            

        entry=ltp

        atint= str(int(closest(lst,entry)))

        tkk_CE=get_symbol('BANKNIFTY',exip,'C',atint)
        tkk_PE=get_symbol('BANKNIFTY',exip,'P',atint)

        # sell both
        st.write('sell tkk_CE and tkk_PE now')

        q=0
        while(q<3):
            try:
                ltp_CE=float(getLTP(tkk_CE,'NFO',fno_symbolList))
            except Exception as e:
                pass
            q+=1
            t.sleep(1)
            
        q=0
        while(q<3):
            try:
                ltp_PE=float(getLTP(tkk_PE,'NFO',fno_symbolList))
            except Exception as e:
                pass
            q+=1
            t.sleep(1)
        
        lis=[]
        sl_CE=ltp_CE+40
        sl_PE=ltp_PE+40
        st.write(datetime.now())
        st.write('sell '+tkk_CE+' at '+str(ltp_CE)+' with sl '+str(sl_CE))
        st.write('sell '+tkk_PE+' at '+str(ltp_PE)+' with sl '+str(sl_PE))
        entry_CE=ltp_CE
        entry_PE=ltp_PE

        
        placeOrder(tkk_CE,'S',qty)
        placeOrder(tkk_PE,'S',qty)

        profit=0
        prof=0
        cnt=0
        lis.append({'Strike':tkk_CE,'Entry':entry_CE,'Stop':sl_CE,'Entry_time':datetime.now()})
        lis.append({'Strike':tkk_PE,'Entry':entry_PE,'Stop':sl_PE,'Entry_time':datetime.now()})

        while(ltp_CE<sl_CE and ltp_PE<sl_PE):
            try:
                ltp_CE=float(getLTP(tkk_CE,'NFO',fno_symbolList))
            except Exception as e:
                pass
            
            try:
                ltp_PE=float(getLTP(tkk_PE,'NFO',fno_symbolList))
            except Exception as e:
                pass
            
            profit=prof+entry_CE-ltp_CE + entry_PE-ltp_PE
            tk=datetime.now().time()
            var=tk.minute
            if(var%15==0 and cnt==0):
                st.write(tkk_CE)
                st.write('Profit CE running',entry_CE-ltp_CE)
                st.write(tkk_PE)
                st.write('Profit PE running',entry_PE-ltp_PE)
                
                st.write('Net Profit', profit)
                cnt=1
                
            if(var%15!=0):
                cnt=0
            
            ppfit=get_mtm()
            pt1=datetime.now().time()
            if(pt1>end or ppfit<-900):
                data  = {}
                uni_exit()
                return
            
        '''if(ltp_CE>sl_CE):
            reentry_ce(ltp_CE,sl_CE,tkk_CE,ltp_PE,sl_PE,tkk_PE)
            if(ltp_PE>sl_PE):
                    
                reentry_pe(ltp_CE,sl_CE,tkk_CE,ltp_PE,sl_PE,tkk_PE)
        elif(ltp_PE>sl_PE):
            reentry_pe(ltp_CE,sl_CE,tkk_CE,ltp_PE,sl_PE,tkk_PE)
            if(ltp_CE>sl_CE):
                    
                reentry_ce(ltp_CE,sl_CE,tkk_CE,ltp_PE,sl_PE,tkk_PE)'''
            
        if(ltp_CE>=sl_CE):
            placeOrder(tkk_CE,'B',qty)
            #cost sl
            sl_PE=entry_PE
            st.write('sl hit for '+tkk_CE)
            #sell order
            prof+=entry_CE-ltp_CE
            # rentry
            #lis.append()
            q=0
            while(q<3):
                try:
                    ltp=float(getLTP(tick,'NSE',all_symbols))
                except Exception as e:
                    pass
                q+=1
                t.sleep(1)
                
            atint= str(int(closest(lst,ltp)))

            tkk_CE=get_symbol('BANKNIFTY',exip,'C',atint)
            # buy ce on rentry
            q=0
            while(q<3):
                try:
                    ltp_CE=float(getLTP(tkk_CE,'NFO',fno_symbolList))
                except Exception as e:
                    pass
                q+=1
                t.sleep(1)
                
            sl_CE=ltp_CE+40
            st.write(datetime.now())
            st.write('sell '+tkk_CE+' at '+str(ltp_CE)+' with sl '+str(sl_CE))
            placeOrder(tkk_CE,'S',qty)
            entry_CE=ltp_CE
            lis.append({'Strike':tkk_CE,'Entry':entry_CE,'Stop':sl_CE,'Entry_time':datetime.now()})
            
            cnt=0
            while(ltp_CE<sl_CE and ltp_PE<sl_PE):
                try:
                    ltp_CE=float(getLTP(tkk_CE,'NFO',fno_symbolList))
                except Exception as e:
                    pass
                
                try:
                    ltp_PE=float(getLTP(tkk_PE,'NFO',fno_symbolList))
                except Exception as e:
                    pass
                
                profit=prof+entry_CE-ltp_CE + entry_PE-ltp_PE
                tk=datetime.now().time()
                
                var=tk.minute
                if(var%15==0 and cnt==0):
                    st.write(tkk_CE)
                    st.write('Profit CE running',entry_CE-ltp_CE)
                    st.write(tkk_PE)
                    st.write('Profit PE running',entry_PE-ltp_PE)
                    
                    st.write('Net Profit', profit)
                    cnt=1
                    
                if(var%15!=0):
                    cnt=0
                    
                ppfit=get_mtm()
                pt1=datetime.now().time()
                if(pt1>end or ppfit<-900):
                    data  = {}
                    uni_exit()
                    return
                    
            if(ltp_CE>=sl_CE):
                placeOrder(tkk_CE,'B',qty)
                # sl hit
                st.write('sl hit for '+tkk_CE)
                #exit order
                prof+=entry_CE-ltp_CE
                
                cnt=0    
                while(ltp_PE<sl_PE):
                    try:
                        ltp_PE=float(getLTP(tkk_PE,'NFO',fno_symbolList))
                    except Exception as e:
                        pass
                    
                    profit=prof+entry_PE-ltp_PE
                    tk=datetime.now().time()
                    var=tk.minute
                    if(var%15==0 and cnt==0):
                        st.write(tkk_PE)
                        st.write('Profit PE running',entry_PE-ltp_PE)
                        
                        
                        st.write('Net Profit', profit)
                        cnt=1
                    if(var%15!=0):
                        cnt=0
                        
                    pt1=datetime.now().time()
                    if(pt1>end):
                        return
                st.write('sl hit for '+tkk_PE)
                placeOrder(tkk_PE,'B',qty)
                #exit order
                prof+=entry_PE-ltp_PE
                # rentry
                q=0
                while(q<3):
                    try:
                        ltp=float(getLTP(tick,'NSE',all_symbols))
                    except Exception as e:
                        pass
                    q+=1
                    t.sleep(1)
                    
                    
                atint= str(int(closest(lst,ltp)))

                tkk_PE=get_symbol('BANKNIFTY',exip,'P',atint)
                # buy PE on rentry
                q=0
                while(q<3):
                    try:
                        ltp_PE=float(getLTP(tkk_PE,'NFO',fno_symbolList))
                    except Exception as e:
                        pass
                    q+=1
                    t.sleep(1)
                    
                sl_PE=ltp_PE+40
                st.write(datetime.now())
                st.write('sell '+tkk_PE+' at '+str(ltp_PE)+' with sl '+str(sl_PE))
                placeOrder(tkk_PE,'S',qty)
                entry_PE=ltp_PE
                
                lis.append({'Strike':tkk_PE,'Entry':entry_PE,'Stop':sl_PE,'Entry_time':datetime.now()})
                
                cnt=0
                while(ltp_PE<sl_PE):
                    try:
                        ltp_PE=float(getLTP(tkk_PE,'NFO',fno_symbolList))
                    except Exception as e:
                        pass
                    
                    profit=prof+entry_PE-ltp_PE 
                    tk=datetime.now().time()
                    var=tk.minute
                    if(var%15==0 and cnt==0):
                        st.write(tkk_PE)
                        st.write('Profit PE running',entry_PE-ltp_PE)
                        
                        
                        st.write('Net Profit', profit)
                        cnt=1
                    if(var%15!=0):
                        cnt=0
                        
                    ppfit=get_mtm()
                    pt1=datetime.now().time()
                    if(pt1>end or ppfit<-900):
                        data  = {}
                        uni_exit()
                        return
                        
                #sl hit
                placeOrder(tkk_PE,'B',qty)
                st.write('sl hit for '+tkk_PE)
                # exit order
                prof+=entry_PE-ltp_PE
                
            elif(ltp_PE>=sl_PE):
                placeOrder(tkk_PE,'B',qty)
                #cost sl
                sl_CE=entry_CE
                st.write('sl hit for '+tkk_PE)
                #sell order
                prof+=entry_PE-ltp_PE
                # rentry
                q=0
                while(q<3):
                    try:
                        ltp=float(getLTP(tick,'NSE',all_symbols))
                    except Exception as e:
                        pass
                    q+=1
                    t.sleep(1)
                    
                    
                atint= str(int(closest(lst,ltp)))

                tkk_PE=get_symbol('BANKNIFTY',exip,'P',atint)
                # buy ce on rentry
                q=0
                while(q<3):
                    try:
                        ltp_PE=float(getLTP(tkk_PE,'NFO',fno_symbolList))
                    except Exception as e:
                        pass
                    q+=1
                    t.sleep(1)
                    
                sl_PE=ltp_PE+40
                st.write(datetime.now())
                st.write('sell '+tkk_PE+' at '+str(ltp_PE)+' with sl '+str(sl_PE))
                placeOrder(tkk_PE,'S',qty)
                entry_PE=ltp_PE
                lis.append({'Strike':tkk_PE,'Entry':entry_PE,'Stop':sl_PE,'Entry_time':datetime.now()})
                
                
                cnt=0
                while(ltp_CE<sl_CE and ltp_PE<sl_PE):
                    try:
                        ltp_CE=float(getLTP(tkk_CE,'NFO',fno_symbolList))
                    except Exception as e:
                        pass
                    
                    try:
                        ltp_PE=float(getLTP(tkk_PE,'NFO',fno_symbolList))
                    except Exception as e:
                        pass
                    
                    profit=prof+entry_CE-ltp_CE + entry_PE-ltp_PE
                    tk=datetime.now().time()
                    
                    var=tk.minute
                    if(var%15==0 and cnt==0):
                        st.write(tkk_CE)
                        st.write('Profit CE running',entry_CE-ltp_CE)
                        st.write(tkk_PE)
                        st.write('Profit PE running',entry_PE-ltp_PE)
                        
                        st.write('Net Profit', profit)
                        cnt=1
                        
                    if(var%15!=0):
                        cnt=0
                        
                    ppfit=get_mtm()
                    pt1=datetime.now().time()
                    if(pt1>end or ppfit<-900):
                        data  = {}
                        uni_exit()
                        return
                        
                if(ltp_PE>=sl_PE):
                    prof+=entry_PE-ltp_PE
                    #exit order
                    placeOrder(tkk_PE,'B',qty)
                    st.write('sl hit for '+tkk_PE)
                    # sl hit
                    cnt=0    
                    while(ltp_CE<sl_CE):
                        try:
                            ltp_CE=float(getLTP(tkk_CE,'NFO',fno_symbolList))
                        except Exception as e:
                            pass
                        
                        profit=prof+entry_CE-ltp_CE 
                        tk=datetime.now().time()
                        
                        var=tk.minute
                        if(var%15==0 and cnt==0):
                            st.write(tkk_CE)
                            st.write('Profit CE running',entry_CE-ltp_CE)
                            
                            
                            st.write('Net Profit', profit)
                            cnt=1
                        if(var%15!=0):
                            cnt=0
                            
                        ppfit=get_mtm()
                        pt1=datetime.now().time()
                        if(pt1>end or ppfit<-900):
                            data  = {}
                            uni_exit()
                            return
                    st.write('sl hit for '+tkk_CE)
                    #exit order
                    placeOrder(tkk_CE,'B',qty)
                    prof+=entry_CE-ltp_CE
                    
                elif(ltp_CE>=sl_CE):
                    placeOrder(tkk_CE,'B',qty)
                    #cost sl
                    sl_PE=entry_PE
                    prof+=entry_CE-ltp_CE
                    #exit order
                    # sl hit
                    st.write('sl hit for '+tkk_CE)
                    cnt=0    
                    while(ltp_PE<sl_PE):
                        try:
                            ltp_PE=float(getLTP(tkk_PE,'NFO',fno_symbolList))
                        except Exception as e:
                            pass
                        
                        profit=prof+entry_PE-ltp_PE 
                        tk=datetime.now().time()
                        var=tk.minute
                        if(var%15==0 and cnt==0):
                            st.write(tkk_PE)
                            st.write('Profit PE running',entry_PE-ltp_PE)
                            
                            
                            st.write('Net Profit', profit)
                            cnt=1
                        if(var%15!=0):
                            cnt=0
                            
                        ppfit=get_mtm()
                        pt1=datetime.now().time()
                        if(pt1>end or ppfit<-900):
                            data  = {}
                            uni_exit()
                            return
                    st.write('sl hit for '+tkk_PE)
                    #exit order
                    placeOrder(tkk_PE,'B',qty)
                    prof+=entry_PE-ltp_PE
                    
                    
        elif(ltp_PE>=sl_PE):
            #cost sl
            sl_CE=entry_CE
            st.write('sl hit for '+tkk_PE)
            #exit order
            placeOrder(tkk_PE,'B',qty)
            prof+=entry_PE-ltp_PE
            # rentry
            q=0
            while(q<3):
                try:
                    ltp=float(getLTP(tick,'NSE',all_symbols))
                except Exception as e:
                    pass
                q+=1
                t.sleep(1)
                
                
            atint= str(int(closest(lst,ltp)))

            tkk_PE=get_symbol('BANKNIFTY',exip,'P',atint)
            # sell pe on rentry
            q=0
            while(q<3):
                try:
                    ltp_PE=float(getLTP(tkk_PE,'NFO',fno_symbolList))
                except Exception as e:
                    pass
                q+=1
                t.sleep(1)
                
            sl_PE=ltp_PE+40
            st.write(datetime.now())
            st.write('sell '+tkk_PE+' at '+str(ltp_PE)+' with sl '+str(sl_PE))
            entry_PE=ltp_PE
            placeOrder(tkk_PE,'S',qty)
            
            lis.append({'Strike':tkk_PE,'Entry':entry_PE,'Stop':sl_PE,'Entry_time':datetime.now()})
            
            
            cnt=0
            while(ltp_CE<sl_CE and ltp_PE<sl_PE):
                try:
                    ltp_CE=float(getLTP(tkk_CE,'NFO',fno_symbolList))
                except Exception as e:
                    pass
                
                try:
                    ltp_PE=float(getLTP(tkk_PE,'NFO',fno_symbolList))
                except Exception as e:
                    pass
                
                profit=prof+entry_CE-ltp_CE + entry_PE-ltp_PE
                tk=datetime.now().time()
                
                var=tk.minute
                if(var%15==0 and cnt==0):
                    st.write(tkk_CE)
                    st.write('Profit CE running',entry_CE-ltp_CE)
                    st.write(tkk_PE)
                    st.write('Profit PE running',entry_PE-ltp_PE)
                    
                    st.write('Net Profit', profit)
                    cnt=1
                    
                if(var%15!=0):
                    cnt=0
                    
                ppfit=get_mtm()
                pt1=datetime.now().time()
                if(pt1>end or ppfit<-900):
                    data  = {}
                    uni_exit()
                    return
            
            if(ltp_PE>=sl_PE):
                st.write('sl hit for '+tkk_PE)
                #exit order
                placeOrder(tkk_PE,'B',qty)
                prof+=entry_PE-ltp_PE
                # sl hit
                cnt=0    
                while(ltp_CE<sl_CE):
                    try:
                        ltp_CE=float(getLTP(tkk_CE,'NFO',fno_symbolList))
                    except Exception as e:
                        pass
                    
                    profit=prof+entry_CE-ltp_CE
                    tk=datetime.now().time()
                    var=tk.minute
                    if(var%15==0 and cnt==0):
                        st.write(tkk_CE)
                        st.write('Profit CE running',entry_CE-ltp_CE)
                        
                        
                        st.write('Net Profit', profit)
                        cnt=1
                    if(var%15!=0):
                        cnt=0
                        
                    ppfit=get_mtm()
                    pt1=datetime.now().time()
                    if(pt1>end or ppfit<-900):
                        data  = {}
                        uni_exit()
                        return
                st.write('sl hit for '+tkk_CE)
                #exit order
                placeOrder(tkk_CE,'B',qty)
                prof+=entry_CE-ltp_CE
                # rentry
                q=0
                while(q<3):
                    try:
                        ltp=float(getLTP(tick,'NSE',all_symbols))
                    except Exception as e:
                        pass
                    q+=1
                    t.sleep(1)
                    
                    
                atint= str(int(closest(lst,ltp)))

                tkk_CE=get_symbol('BANKNIFTY',exip,'C',atint)
                # buy ce on rentry
                q=0
                while(q<3):
                    try:
                        ltp_CE=float(getLTP(tkk_CE,'NFO',fno_symbolList))
                    except Exception as e:
                        pass
                    q+=1
                    t.sleep(1)
                    
                sl_CE=ltp_CE+40
                st.write(datetime.now())
                st.write('sell '+tkk_CE+' at '+str(ltp_CE)+' with sl '+str(sl_CE))
                placeOrder(tkk_CE,'S',qty)
                entry_CE=ltp_CE
                lis.append({'Strike':tkk_CE,'Entry':entry_CE,'Stop':sl_CE,'Entry_time':datetime.now()})
                
                
                cnt=0
                while(ltp_CE<sl_CE):
                    try:
                        ltp_CE=float(getLTP(tkk_CE,'NFO',fno_symbolList))
                    except Exception as e:
                        pass
                    
                    profit=prof+entry_CE-ltp_CE
                    tk=datetime.now().time()
                    var=tk.minute
                    if(var%15==0 and cnt==0):
                        st.write(tkk_CE)
                        st.write('Profit CE running',entry_CE-ltp_CE)
                        
                        
                        st.write('Net Profit', profit)
                        cnt=1
                    if(var%15!=0):
                        cnt=0
                        
                    ppfit=get_mtm()
                    pt1=datetime.now().time()
                    if(pt1>end or ppfit<-900):
                        data  = {}
                        uni_exit()
                        return
                        
                #sl hit
                st.write('sl hit for '+tkk_CE)
                # exit order
                placeOrder(tkk_CE,'B',qty)
                prof+=entry_CE-ltp_CE
                

            elif(ltp_CE>=sl_CE):
                #cost sl
                sl_PE=entry_PE
                st.write('sl hit for '+tkk_CE)
                #exit order
                placeOrder(tkk_CE,'B',qty)
                prof+=entry_CE-ltp_CE
                # rentry
                q=0
                while(q<3):
                    try:
                        ltp=float(getLTP(tick,'NSE',all_symbols))
                    except Exception as e:
                        pass
                    q+=1
                    t.sleep(1)
                    
                    
                atint= str(int(closest(lst,ltp)))

                tkk_CE=get_symbol('BANKNIFTY',exip,'C',atint)
                # sell ce on rentry
                q=0
                while(q<3):
                    try:
                        ltp_CE=float(getLTP(tkk_CE,'NFO',fno_symbolList))
                    except Exception as e:
                        pass
                    q+=1
                    t.sleep(1)
                    
                sl_CE=ltp_CE+40
                st.write(datetime.now())
                st.write('sell '+tkk_CE+' at '+str(ltp_CE)+' with sl '+str(sl_CE))
                placeOrder(tkk_CE,'S',qty)
                entry_CE=ltp_CE
                lis.append({'Strike':tkk_CE,'Entry':entry_CE,'Stop':sl_CE,'Entry_time':datetime.now()})
                
                
                cnt=0
                while(ltp_CE<sl_CE and ltp_PE<sl_PE):
                    try:
                        ltp_CE=float(getLTP(tkk_CE,'NFO',fno_symbolList))
                    except Exception as e:
                        pass
                    
                    try:
                        ltp_PE=float(getLTP(tkk_PE,'NFO',fno_symbolList))
                    except Exception as e:
                        pass
                    
                    profit=prof+entry_CE-ltp_CE + entry_PE-ltp_PE
                    tk=datetime.now().time()
                    
                    var=tk.minute
                    if(var%15==0 and cnt==0):
                        st.write(tkk_CE)
                        st.write('Profit CE running',entry_CE-ltp_CE)
                        st.write(tkk_PE)
                        st.write('Profit PE running',entry_PE-ltp_PE)
                        
                        st.write('Net Profit', profit)
                        cnt=1
                        
                    if(var%15!=0):
                        cnt=0
                        
                    ppfit=get_mtm()
                    pt1=datetime.now().time()
                    if(pt1>end or ppfit<-900):
                        data  = {}
                        uni_exit()
                        return
                        
                if(ltp_PE>=sl_PE):
                    #cost sl
                    sl_CE=entry_CE
                    prof+=entry_PE-ltp_PE
                    #exit order
                    placeOrder(tkk_PE,'B',qty)
                    st.write('sl hit for '+tkk_PE)
                    # sl hit
                    cnt=0    
                    while(ltp_CE<sl_CE):
                        try:
                            ltp_CE=float(getLTP(tkk_CE,'NFO',fno_symbolList))
                        except Exception as e:
                            pass
                        
                        profit=prof+entry_CE-ltp_CE
                        tk=datetime.now().time()
                        var=tk.minute
                        if(var%15==0 and cnt==0):
                            st.write(tkk_CE)
                            st.write('Profit CE running',entry_CE-ltp_CE)
                            
                            
                            st.write('Net Profit', profit)
                            cnt=1
                        if(var%15!=0):
                            cnt=0
                            
                        ppfit=get_mtm()
                        pt1=datetime.now().time()
                        if(pt1>end or ppfit<-900):
                            data  = {}
                            uni_exit()
                            return
                    st.write('sl hit for '+tkk_CE)
                    #exit order
                    placeOrder(tkk_CE,'B',qty)
                    prof+=entry_CE-ltp_CE
                    
                elif(ltp_CE>=sl_CE):
                    prof+=entry_CE-ltp_CE
                    #exit order
                    placeOrder(tkk_CE,'B',qty)
                    # sl hit
                    st.write('sl hit for '+tkk_CE)
                    cnt=0    
                    while(ltp_PE<sl_PE):
                        try:
                            ltp_PE=float(getLTP(tkk_PE,'NFO',fno_symbolList))
                        except Exception as e:
                            pass
                        
                        profit=prof+entry_PE-ltp_PE 
                        tk=datetime.now().time()
                        var=tk.minute
                        if(var%15==0 and cnt==0):
                            st.write(tkk_PE)
                            st.write('Profit PE running',entry_PE-ltp_PE)
                            
                            
                            st.write('Net Profit', profit)
                            cnt=1
                        if(var%15!=0):
                            cnt=0
                            
                        pt1=datetime.now().time()
                        
                        ppfit=get_mtm()
                        pt1=datetime.now().time()
                        if(pt1>end or ppfit<-900):
                            data  = {}
                            uni_exit()
                            return
                    st.write('sl hit for '+tkk_PE)
                    #exit order
                    placeOrder(tkk_PE,'B',qty)
                    prof+=entry_PE-ltp_PE

    # get atmStrike ce & pe
    symbol = st.text_input("Enter the symbol/ instrument (like 'NIFTY BANK')")
    strikeExp = st.text_input("Enter the strike expiry (every thrusday/like '01-NOV-2023') ")
    strikeSymbol = st.text_input("Enter strike symbol (like 'BANKNIFTY') ")
    if symbol and strikeExp and strikeSymbol:

        atm=float(getLTP(symbol, 'NSE', all_symbols))
        st.write("Atm value : ",atm)

        fno_symbols=pd.read_csv('https://api.shoonya.com/NFO_symbols.txt.zip')
        fno_symbolList = fno_symbols[(fno_symbols['Expiry'] == '01-NOV-2023') & (fno_symbols['Symbol'] =='BANKNIFTY') ]
        lst=fno_symbolList['StrikePrice'].tolist()

        strikeButton = st.button("Calculate Closest Strike ")
        if strikeButton:
            strike=str(int(closest(lst,atm)))
            st.write("Closest Strike at the money: ", strike)

    # function call straddle for buy & sell at same strike price
    straExp = st.text_input("Enter the expiry (like 01NOV23): ")
    straLot = st.number_input("Enter no. of lots: ", min_value=1, step=1)
    straddleButton = st.button("Run algorithm")
    if straddleButton:
        straddle(straExp,straLot)  