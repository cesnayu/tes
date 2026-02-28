import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
import math

# Konfigurasi Halaman (Wide Mode)
st.set_page_config(page_title="Dashboard Saham OHLC & Volume", layout="wide")

# --- 1. FITUR CACHING & FETCH REAL DATA (OHLC + VOLUME) ---
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_real_stock_data(tickers, time_range):
    period_map = {'1w': '5d', '1m': '1mo', '3m': '3mo'}
    period = period_map[time_range]
    
    stocks = []
    
    for ticker in tickers:
        try:
            # Mengambil data lengkap termasuk Volume
            stock_data = yf.Ticker(ticker).history(period=period)
            
            if not stock_data.empty:
                # Membuat DataFrame bersih dengan OHLCV
                df = pd.DataFrame({
                    'Tanggal': stock_data.index.date,
                    'Open': stock_data['Open'].values,
                    'High': stock_data['High'].values,
                    'Low': stock_data['Low'].values,
                    'Close': stock_data['Close'].values,
                    'Volume': stock_data['Volume'].values
                })
                
                # Konversi Volume ke Lot (1 Lot = 100 Lembar)
                df['Volume_Lot'] = df['Volume'] / 100
                
                stocks.append({
                    'name': ticker.upper(),
                    'data': df,
                    'min_price': df['Low'].min(),       # Harga terendah di periode tersebut
                    'max_price': df['High'].max(),      # Harga tertinggi di periode tersebut
                    'min_vol_lot': df['Volume_Lot'].min() # Volume lot terkecil di periode tersebut
                })
        except Exception as e:
            pass 
            
    return stocks

# --- 2. KOMPONEN GRAFIK (KOLOM + HIGH-LOW + DARK MODE) ---
def draw_chart(stock):
    df = stock['data'].copy()
    
    # Kalkulasi Persentase Relatif Terhadap Open
    df['Body_%'] = (df['Close'] - df['Open']) / df['Open'] * 100
    df['High_Rel_%'] = (df['High'] - df['Open']) / df['Open'] * 100
    df['Low_Rel_%'] = (df['Low'] - df['Open']) / df['Open'] * 100
    
    # Warna Kolom: Hijau (Naik dari Open), Merah (Turun dari Open)
    colors = ['#10b981' if val >= 0 else '#ef4444' for val in df['Body_%']]
    
    # Warna Garis High-Low: Emas agar kontras dengan Hitam
    wick_color = '#FFD700' 
    
    fig = go.Figure()
    
    # TRACE 1: GARIS HIGH-LOW (Di belakang kolom)
    wick_x, wick_y = [], []
    for i, row in df.iterrows():
        wick_x.extend([row['Tanggal'], row['Tanggal'], None])
        wick_y.extend([row['Low_Rel_%'], row['High_Rel_%'], None])
        
    fig.add_trace(go.Scatter(
        x=wick_x,
        y=wick_y,
        mode='lines',
        line=dict(color=wick_color, width=1),
        name='Range High-Low',
        hoverinfo='skip' 
    ))
    
    # TRACE 2: KOLOM RETURN (Open ke Close)
    fig.add_trace(go.Bar(
        x=df['Tanggal'], 
        y=df['Body_%'],
        marker_color=colors,
        name='Open-to-Close Return',
        # Tooltip ditambahkan Volume Lot
        hovertemplate=(
            '<b>Tanggal: %{x}</b><br>' +
            'Return (O-C): %{y:.2f}%<br>' +
            '<span style="color:gray;">--------------------</span><br>' +
            'Open: %{customdata[0]:,.0f}<br>' +
            'High: %{customdata[1]:,.0f}<br>' +
            'Low: %{customdata[2]:,.0f}<br>' +
            'Close: %{customdata[3]:,.0f}<br>' +
            'Volume: %{customdata[4]:,.0f} Lot<extra></extra>'
        ),
        # Mengirim data OHLC dan Volume Lot ke tooltip
        customdata=df[['Open', 'High', 'Low', 'Close', 'Volume_Lot']].values 
    ))
    
    # Konfigurasi Tema Dark Mode dan Header Informasi
    header_text = (
        f"<b>{stock['name']}</b><br>"
        f"<span style='font-size: 12px; color: #ef4444;'>Min Harga: {stock['min_price']:,.0f}</span> | "
        f"<span style='font-size: 12px; color: #10b981;'>Max Harga: {stock['max_price']:,.0f}</span> | "
        f"<span style='font-size: 12px; color: #60a5fa;'>Min Vol: {stock['min_vol_lot']:,.0f} Lot</span>"
    )

    fig.update_layout(
        template="plotly_dark", 
        title={
            'text': header_text,
            'y':0.9, 'x':0.05, 'xanchor': 'left', 'yanchor': 'top'
        },
        margin=dict(l=20, r=20, t=65, b=20),
        height=280, 
        xaxis_title="",
        yaxis_title="Return vs Open (%)",
        paper_bgcolor="black", 
        plot_bgcolor="black",
        showlegend=False, 
    )
    
    # Grid dan Garis Nol
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#222222')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#222222', zeroline=True, zerolinewidth=1, zerolinecolor='#555555')
    
    return fig

# --- 3. UI DASHBOARD ---
st.title("📊 Dashboard Saham Intraday Return (OHLC & Volume)")

default_stocks = "BREN.jk, BBCA.jk, DSSA.jk, BBRI.jk, TPIA.jk, DCII.jk, BYAN.jk, AMMN.jk, BMRI.jk, TLKM.jk, ASII.jk, MORA.jk, SRAJ.jk, CUAN.jk, BRPT.jk, BBNI.jk, PANI.jk, BNLI.jk, BRMS.jk, CDIA.jk, DNET.jk, IMPC.jk, FILM.jk, MPRO.jk, BRIS.jk, ICBP.jk, HMSP.jk, BUMI.jk, EMAS.jk, UNTR.jk, ANTM.jk, NCKL.jk, SMMA.jk, ADMR.jk, CASA.jk, UNVR.jk, RISE.jk, CPIN.jk, MLPT.jk, AMRT.jk, MDKA.jk, ISAT.jk, MBMA.jk, GOTO.jk, INCO.jk, AADI.jk, INDF.jk, PTRO.jk, BELI.jk, ADRO.jk, EXCL.jk, TCPI.jk, KLBF.jk, EMTK.jk, MYOR.jk, PGAS.jk, INKP.jk, PGUN.jk, PGEO.jk, GEMS.jk, MTEL.jk, BNGA.jk, CMRY.jk, ARCI.jk, TBIG.jk, MEGA.jk, SILO.jk, MEDC.jk, GIAA.jk, SOHO.jk, VKTR.jk, CBDK.jk, MIKA.jk, NISP.jk, JPFA.jk, GGRM.jk, TOWR.jk, BBHI.jk, ENRG.jk, TAPG.jk, SUPA.jk, BUVA.jk, PTBA.jk, BINA.jk, COIN.jk, AVIA.jk, JSMR.jk, AKRA.jk, NSSS.jk, PNBN.jk, ITMG.jk, BDMN.jk, ARKO.jk, MDIY.jk, TINS.jk, BSIM.jk, INTP.jk, JARR.jk, BKSL.jk, BTPN.jk, ARTO.jk, FAPA.jk, MKPI.jk, RMKE.jk, SRTG.jk, TKIM.jk, MAPA.jk, MSIN.jk, MAPI.jk, RLCO.jk, HEAL.jk, BSDE.jk, KPIG.jk, CITA.jk, PWON.jk, BNBR.jk, APIC.jk, BBTN.jk, SMGR.jk, RAJA.jk, POLU.jk, LIFE.jk, BNII.jk, INDY.jk, CTRA.jk, SMAR.jk, SCMA.jk, SSMS.jk, CARE.jk, ULTJ.jk, SIDO.jk, DSNG.jk, BBSI.jk, BUKA.jk, AALI.jk, RATU.jk, BBKP.jk, HRUM.jk, CMNT.jk, SGRO.jk, PSAB.jk, JRPT.jk, YUPI.jk, STAA.jk, STTP.jk, GOOD.jk, MCOL.jk, WIFI.jk, AUTO.jk, TSPC.jk, NICL.jk, ALII.jk, SHIP.jk, MLBI.jk, PACK.jk, DEWA.jk, CYBR.jk, PRAY.jk, POWR.jk, ESSA.jk, BMAS.jk, MIDI.jk, EDGE.jk, BIPI.jk, BSSR.jk, SMSM.jk, ADMF.jk, ELPI.jk, BFIN.jk, HRTA.jk, CLEO.jk, BTPS.jk, CMNP.jk, CNMA.jk, BANK.jk, ADES.jk, INPP.jk, BJBR.jk, SIMP.jk, BJTM.jk, PNLF.jk, INET.jk, SINI.jk, TLDN.jk, GMFI.jk, NATO.jk, BBMD.jk, LSIP.jk, TMAS.jk, ABMM.jk, DUTI.jk, BHAT.jk, DAAZ.jk, SGER.jk, DMND.jk, CLAY.jk, IBST.jk, MTDL.jk, BULL.jk, ACES.jk, LPKR.jk, DMAS.jk, SMRA.jk, SSIA.jk, ERAA.jk, EPMT.jk, SMDR.jk, KRAS.jk, JSPT.jk, BOGA.jk, MAYA.jk, AGII.jk, OMED.jk, PALM.jk, ANJT.jk, TOBA.jk, DATA.jk, BESS.jk, INDS.jk, CASS.jk, ELSA.jk, AGRO.jk, SAME.jk, UANG.jk, MNCN.jk, LINK.jk, BPII.jk, YULE.jk, TRIN.jk, BALI.jk, UDNG.jk, PBSA.jk, CTBN.jk, DRMA.jk, NIRO.jk, DKFT.jk, GTSI.jk, MTLA.jk, BBYB.jk, TFCO.jk, ROTI.jk, FISH.jk, TRIM.jk, PYFA.jk, TGKA.jk, GOLF.jk, KIJA.jk, JTPE.jk, MASB.jk, HUMI.jk, FORE.jk, MPMX.jk, RDTX.jk, MSTI.jk, BSWD.jk, IMAS.jk, BIRD.jk, LPCK.jk, ASSA.jk, TUGU.jk, BWPT.jk, WIIM.jk, RONY.jk, LPPF.jk, CENT.jk, SDRA.jk, SURE.jk, VICI.jk, MGLV.jk, NOBU.jk, KEEN.jk, PSGO.jk, AMAR.jk, CPRO.jk, CBRE.jk, SOCI.jk, ARNA.jk, TBLA.jk, STAR.jk, GJTL.jk, VICO.jk, PBID.jk, INPC.jk, GGRP.jk, IRSX.jk, AGRS.jk, HEXA.jk, TOTL.jk, UNIC.jk, SMMT.jk, BUKK.jk, ROCK.jk, SKRN.jk, MDLA.jk, MMLP.jk, MINA.jk, BACA.jk, MAPB.jk, KEJU.jk, BGTG.jk, SOTS.jk, MBSS.jk, SAMF.jk, BHIT.jk, ARGO.jk, CBUT.jk, PNIN.jk, MARK.jk, SMDM.jk, ISSP.jk, FPNI.jk, APLN.jk, MYOH.jk, ASRI.jk, SMIL.jk, DAYA.jk, KAEF.jk, IFSH.jk, BNBA.jk, RALS.jk, JAWA.jk, MCOR.jk, PKPK.jk, HATM.jk, TOTO.jk, BCIC.jk, IATA.jk, MAHA.jk, FOLK.jk, SMBR.jk, SFAN.jk, BISI.jk, BABP.jk, FUTR.jk, PSKT.jk, OASA.jk, ASLI.jk, SSTM.jk, SIPD.jk, MGRO.jk, PORT.jk, DNAR.jk, MKAP.jk, BVIC.jk, BOLT.jk, PNGO.jk, IPCC.jk, BLTZ.jk, ASGR.jk, POLI.jk, DWGL.jk, BMTR.jk, GMTD.jk, WINS.jk, IFII.jk, MSJA.jk, BCAP.jk, OMRE.jk, BEEF.jk, KMTR.jk, NICE.jk, BKSW.jk, PRDA.jk, DOID.jk, TRUE.jk, BLUE.jk, MDIA.jk, WOOD.jk, ACST.jk, IMJS.jk, AMAG.jk, PTPP.jk, MTMH.jk, CSRA.jk, MLIA.jk, ITMA.jk, DGWG.jk, KETR.jk, NRCA.jk, DMMX.jk, SCCO.jk, INDR.jk, PNBS.jk, BRAM.jk, LUCY.jk, MBAP.jk, TPMA.jk, ELTY.jk, IPTV.jk, STRK.jk, TEBE.jk, ADHI.jk, LPGI.jk, SUNI.jk, HILL.jk, PSSI.jk, MINE.jk, FAST.jk, DVLA.jk, ERAL.jk, HERO.jk, KINO.jk, CSAP.jk, UCID.jk, IPCM.jk, MLPL.jk, VISI.jk, PTSN.jk, BBRM.jk, SPTO.jk, FMII.jk, PPRE.jk, MAIN.jk, AYAM.jk, EURO.jk, SKLT.jk, DEPO.jk, BSBK.jk, MKTR.jk, BMHS.jk, NEST.jk, PMJS.jk, BEKS.jk, KKGI.jk, DLTA.jk, AMFG.jk, RAAM.jk, TRGU.jk, ALDO.jk, GWSA.jk, PSAT.jk, GSMF.jk, CARS.jk, PADI.jk, BBLD.jk, DOOH.jk, ABDA.jk, BELL.jk, NETV.jk, MERK.jk, BLOG.jk, DILD.jk, TAMU.jk, CEKA.jk, ATIC.jk, TRST.jk, SONA.jk, BBSS.jk, KBLI.jk, BLES.jk, CFIN.jk, JKON.jk, TIFA.jk, CAMP.jk, RANC.jk, MITI.jk, TCID.jk, WSBP.jk, GZCO.jk, AISA.jk, CITY.jk, JIHD.jk, LTLS.jk, IBOS.jk, ADCP.jk, ARTA.jk, BUAH.jk, INDO.jk, WOMF.jk, BEST.jk, PANS.jk, TBMS.jk, ENAK.jk, RSCH.jk, BLTA.jk, JGLE.jk, MTWI.jk, ARII.jk, BTEK.jk, AREA.jk, BOLA.jk, SHID.jk, ZINC.jk, ASLC.jk, PEVE.jk, LIVE.jk, MMIX.jk, GHON.jk, CHIP.jk, WIRG.jk, GDST.jk, PBRX.jk, GRIA.jk, ATAP.jk, CMPP.jk, NELY.jk, RMKO.jk, NICK.jk, SMGA.jk, SPMA.jk, RELI.jk, HGII.jk, BUDI.jk, SKBM.jk, COCO.jk, LEAD.jk, VOKS.jk, PDPP.jk, MHKI.jk, NFCX.jk, PTPW.jk, PJAA.jk, ZATA.jk, NIKL.jk, FUJI.jk, AMOR.jk, PANR.jk, ADMG.jk, MGNA.jk, TALF.jk, AMAN.jk, BABY.jk, MTFN.jk, WTON.jk, IPOL.jk, SULI.jk, PMUI.jk, KSIX.jk, PADA.jk, LFLO.jk, BPFI.jk, JECC.jk, FORU.jk, HDFA.jk, KOKA.jk, BDKR.jk, DGIK.jk, WMUU.jk, PGJO.jk, RODA.jk, KDSI.jk, AXIO.jk, TIRA.jk, MDLN.jk, MOLI.jk, BEER.jk, HOKI.jk, BRNA.jk, GTBO.jk, BIKE.jk, UNIQ.jk, MPPA.jk, APEX.jk, AHAP.jk, GTRA.jk, SWID.jk, IKBI.jk, HOMI.jk, HOPE.jk, EKAD.jk, VIVA.jk, UNSP.jk, PEGE.jk, PZZA.jk, SOFA.jk, IRRA.jk, ELIT.jk, WEGE.jk, SOSS.jk, AWAN.jk, SMKL.jk, GLVA.jk, TRIS.jk, KOTA.jk, GUNA.jk, HAIS.jk, UNTD.jk, CHEK.jk, LABS.jk, BOAT.jk, PNSE.jk, MREI.jk, FITT.jk, KONI.jk, VTNY.jk, URBN.jk, TRON.jk, IDPR.jk, WINE.jk, DART.jk, PJHB.jk, GPRA.jk, MDKI.jk, KING.jk, CNKO.jk, UFOE.jk, BSML.jk, VERN.jk, HALO.jk, COAL.jk, APLI.jk, CRAB.jk, ESTA.jk, SURI.jk, MDRN.jk, MAXI.jk, KMDS.jk, CLPI.jk, BAYU.jk, VRNA.jk, TIRT.jk, IGAR.jk, LAPD.jk, IKPM.jk, SCNP.jk, MCAS.jk, REAL.jk, RIGS.jk, CCSI.jk, GDYR.jk, GULA.jk, NASA.jk, PDES.jk, CSIS.jk, GOLD.jk, PTPS.jk, CBPE.jk, SOLA.jk, TYRE.jk, ZONE.jk, BIPP.jk, BKDP.jk, ESTI.jk, IOTF.jk, LPLI.jk, VAST.jk, HYGN.jk, ASRM.jk, KREN.jk, SMLE.jk, DYAN.jk, DGNS.jk, EAST.jk, HAJJ.jk, TFAS.jk, SRSN.jk, JATI.jk, KBLM.jk, DADA.jk, BMSR.jk, KOBX.jk, NAIK.jk, KBAG.jk, TARA.jk, SATU.jk, ASPR.jk, ASHA.jk, YOII.jk, UVCR.jk, CRSN.jk, YPAS.jk, TRUS.jk, ATLA.jk, INTA.jk, ERTX.jk, GPSO.jk, PART.jk, MUTU.jk, SAFE.jk, KLAS.jk, AKPI.jk, ITIC.jk, CGAS.jk, EMDE.jk, MICE.jk, VINS.jk, ASMI.jk, HRME.jk, BPTR.jk, AMIN.jk, ASPI.jk, IKAI.jk, BINO.jk, SAGE.jk, TOSK.jk, BTON.jk, OKAS.jk, MPXL.jk, WGSH.jk, ACRO.jk, AGAR.jk, INOV.jk, POLA.jk, LMPI.jk, FIRE.jk, ANDI.jk, PUDP.jk, DOSS.jk, FWCT.jk, AKSI.jk, CASH.jk, KBLV.jk, PRIM.jk, NTBK.jk, DEWI.jk, OBAT.jk, ASJT.jk, ALKA.jk, ECII.jk, RELF.jk, LCKM.jk, PEHA.jk, AKKU.jk, ENZO.jk, AYLS.jk, INPS.jk, BAJA.jk, WINR.jk, ASDM.jk, SDPC.jk, TRJA.jk, SAPX.jk, WAPO.jk, PTMP.jk, BAUT.jk, MEJA.jk, JMAS.jk, LPPS.jk, OBMD.jk, NPGF.jk, NZIA.jk, MANG.jk, LION.jk, TAXI.jk, PTSP.jk, APII.jk, CAKK.jk, NANO.jk, SLIS.jk, DFAM.jk, WOWS.jk, SDMU.jk, CINT.jk, ZYRX.jk, DKHH.jk, MRAT.jk, ABBA.jk, BOBA.jk, DIVA.jk, PURA.jk, MARI.jk, PAMG.jk, BAPI.jk, CANI.jk, KOPI.jk, DSFI.jk, SMKM.jk, WEHA.jk, PURI.jk, LPIN.jk, IBFN.jk, RUIS.jk, NAYZ.jk, LAJU.jk, TRUK.jk, LAND.jk, KARW.jk, HELI.jk, CHEM.jk, SEMA.jk, PSDN.jk, IPAC.jk, SNLK.jk, INTD.jk, MSKY.jk, MBTO.jk, KRYA.jk, ASBI.jk, INCI.jk, TMPO.jk, GEMA.jk, ISAP.jk, YELO.jk, MERI.jk, PTIS.jk, ISEA.jk, FOOD.jk, LABA.jk, MPIX.jk, RGAS.jk, DEFI.jk, KUAS.jk, SBMA"
user_input = st.text_area("✍️ Masukkan Kode Saham (Pisahkan dengan koma):", default_stocks, height=100)

ticker_list = [ticker.strip().upper() for ticker in user_input.split(',')]
ticker_list = [t for t in ticker_list if t]

total_stocks = len(ticker_list)
total_pages = math.ceil(total_stocks / 20) if total_stocks > 0 else 1

if 'page' not in st.session_state:
    st.session_state.page = 1

if st.session_state.page > total_pages:
    st.session_state.page = total_pages

col_filter, col_spacer, col_prev, col_page, col_next = st.columns([4, 3, 1, 1, 1])

with col_filter:
    time_range = st.radio(
        "Pilih Rentang Waktu:",
        ['1w', '1m', '3m'],
        format_func=lambda x: '1 Minggu' if x == '1w' else '1 Bulan' if x == '1m' else '3 Bulan',
        horizontal=True
    )

with col_prev:
    if st.button("⬅️ Prev", use_container_width=True, disabled=(st.session_state.page <= 1)):
        st.session_state.page -= 1
        st.rerun()

with col_page:
    st.markdown(f"<div style='text-align: center; padding-top: 8px; font-weight: bold;'>Hal {st.session_state.page} / {total_pages}</div>", unsafe_allow_html=True)

with col_next:
    if st.button("Next ➡️", use_container_width=True, disabled=(st.session_state.page >= total_pages)):
        st.session_state.page += 1
        st.rerun()

st.divider()

if total_stocks == 0:
    st.warning("Silakan masukkan minimal 1 kode saham.")
else:
    start_idx = (st.session_state.page - 1) * 20
    end_idx = start_idx + 20
    current_page_tickers = ticker_list[start_idx:end_idx]

    with st.spinner(f'Mengambil data OHLCV untuk {len(current_page_tickers)} saham...'):
        stocks_data = fetch_real_stock_data(current_page_tickers, time_range)

    if not stocks_data:
        st.error("Gagal mengambil data. Pastikan kode saham benar.")
    else:
        for i in range(0, len(stocks_data), 2):
            cols = st.columns(2)
            with cols[0]:
                st.plotly_chart(draw_chart(stocks_data[i]), use_container_width=True, theme=None) 
            with cols[1]:
                if i + 1 < len(stocks_data):
                    st.plotly_chart(draw_chart(stocks_data[i+1]), use_container_width=True, theme=None)
