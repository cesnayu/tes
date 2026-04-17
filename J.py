import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go

# Mengatur layout halaman menjadi lebar
st.set_page_config(layout="wide", page_title="Dashboard Saham")
st.title("📊 Dashboard Analisis Saham")

# Membuat dua tab
tab1, tab2 = st.tabs(["📋 Tabel Perbandingan (3 & 12 Bulan)", "📈 Grafik Harga Saham"])

# ==========================================
# TAB 1: TABEL PERBANDINGAN
# ==========================================
with tab1:
    st.write("Membandingkan harga penutupan saat ini dengan posisi 3 bulan dan 12 bulan yang lalu.")
    
    default_tickers = "BREN.JK, BBCA.JK, DSSA.JK, BBRI.JK, TPIA.JK, DCII.JK, BYAN.JK, AMMN.JK, BMRI.JK, TLKM.JK, ASII.JK, MORA.JK, SRAJ.JK, CUAN.JK, BRPT.JK, BBNI.JK, PANI.JK, BNLI.JK, BRMS.JK, CDIA.JK, DNET.JK, IMPC.JK, FILM.JK, MPRO.JK, BRIS.JK, ICBP.JK, HMSP.JK, BUMI.JK, EMAS.JK, UNTR.JK, ANTM.JK, NCKL.JK, SMMA.JK, ADMR.JK, CASA.JK, UNVR.JK, RISE.JK, CPIN.JK, MLPT.JK, AMRT.JK, MDKA.JK, ISAT.JK, MBMA.JK, GOTO.JK, INCO.JK, AADI.JK, INDF.JK, PTRO.JK, BELI.JK, ADRO.JK, EXCL.JK, TCPI.JK, KLBF.JK, EMTK.JK, MYOR.JK, PGAS.JK, INKP.JK, PGUN.JK, PGEO.JK, GEMS.JK, MTEL.JK, BNGA.JK, CMRY.JK, ARCI.JK, TBIG.JK, MEGA.JK, SILO.JK, MEDC.JK, GIAA.JK, SOHO.JK, VKTR.JK, CBDK.JK, MIKA.JK, NISP.JK, JPFA.JK, GGRM.JK, TOWR.JK, BBHI.JK, ENRG.JK, TAPG.JK, SUPA.JK, BUVA.JK, PTBA.JK, BINA.JK, COIN.JK, AVIA.JK, JSMR.JK, AKRA.JK, NSSS.JK, PNBN.JK, ITMG.JK, BDMN.JK, ARKO.JK, MDIY.JK, TINS.JK, BSIM.JK, INTP.JK, JARR.JK, BKSL.JK, BTPN.JK, ARTO.JK, FAPA.JK, MKPI.JK, RMKE.JK, SRTG.JK, TKIM.JK, MAPA.JK, MSIN.JK, MAPI.JK, RLCO.JK, HEAL.JK, BSDE.JK, KPIG.JK, CITA.JK, PWON.JK, BNBR.JK, APIC.JK, BBTN.JK, SMGR.JK, RAJA.JK, POLU.JK, LIFE.JK, BNII.JK, INDY.JK, CTRA.JK, SMAR.JK, SCMA.JK, SSMS.JK, CARE.JK, ULTJ.JK, SIDO.JK, DSNG.JK, BBSI.JK, BUKA.JK, AALI.JK, RATU.JK, BBKP.JK, HRUM.JK, CMNT.JK, SGRO.JK, PSAB.JK, JRPT.JK, YUPI.JK, STAA.JK, STTP.JK, GOOD.JK, MCOL.JK, WIFI.JK, AUTO.JK, TSPC.JK, NICL.JK, ALII.JK, SHIP.JK, MLBI.JK, PACK.JK, DEWA.JK, CYBR.JK, PRAY.JK, POWR.JK, ESSA.JK, BMAS.JK, MIDI.JK, EDGE.JK, BIPI.JK, BSSR.JK, SMSM.JK, ADMF.JK, ELPI.JK, BFIN.JK, HRTA.JK, CLEO.JK, BTPS.JK, CMNP.JK, CNMA.JK, BANK.JK, ADES.JK, INPP.JK, BJBR.JK, SIMP.JK, BJTM.JK, PNLF.JK, INET.JK, SINI.JK, TLDN.JK, GMFI.JK, NATO.JK, BBMD.JK, LSIP.JK, TMAS.JK, ABMM.JK, DUTI.JK, BHAT.JK, DAAZ.JK, SGER.JK, DMND.JK, CLAY.JK, IBST.JK, MTDL.JK, BULL.JK, ACES.JK, LPKR.JK, DMAS.JK, SMRA.JK, SSIA.JK, ERAA.JK, EPMT.JK, SMDR.JK, KRAS.JK, JSPT.JK, BOGA.JK, MAYA.JK, AGII.JK, OMED.JK, PALM.JK, ANJT.JK, TOBA.JK, DATA.JK, BESS.JK, INDS.JK, CASS.JK, ELSA.JK, AGRO.JK, SAME.JK, UANG.JK, MNCN.JK, LINK.JK, BPII.JK, YULE.JK, TRIN.JK, BALI.JK, UDNG.JK, PBSA.JK, CTBN.JK, DRMA.JK, NIRO.JK, DKFT.JK, GTSI.JK, MTLA.JK, BBYB.JK, TFCO.JK, ROTI.JK, FISH.JK, TRIM.JK, PYFA.JK, TGKA.JK, GOLF.JK, KIJA.JK, JTPE.JK, MASB.JK, HUMI.JK, FORE.JK, MPMX.JK, RDTX.JK, MSTI.JK, BSWD.JK, IMAS.JK, BIRD.JK, LPCK.JK, ASSA.JK, TUGU.JK, BWPT.JK, WIIM.JK, RONY.JK, LPPF.JK, CENT.JK, SDRA.JK, SURE.JK, VICI.JK, MGLV.JK, NOBU.JK, KEEN.JK, PSGO.JK, AMAR.JK, CPRO.JK, CBRE.JK, SOCI.JK, ARNA.JK, TBLA.JK, STAR.JK, GJTL.JK, VICO.JK, PBID.JK, INPC.JK, GGRP.JK, IRSX.JK, AGRS.JK, HEXA.JK, TOTL.JK, UNIC.JK, SMMT.JK, BUKK.JK, ROCK.JK, SKRN.JK, MDLA.JK, MMLP.JK, MINA.JK, BACA.JK, MAPB.JK, KEJU.JK, BGTG.JK, SOTS.JK, MBSS.JK, SAMF.JK, BHIT.JK, ARGO.JK, CBUT.JK, PNIN.JK, MARK.JK, SMDM.JK, ISSP.JK, FPNI.JK, APLN.JK, MYOH.JK, ASRI.JK, SMIL.JK, DAYA.JK, KAEF.JK, IFSH.JK, BNBA.JK, RALS.JK, JAWA.JK, MCOR.JK, PKPK.JK, HATM.JK, TOTO.JK, BCIC.JK, IATA.JK, MAHA.JK, FOLK.JK, SMBR.JK, SFAN.JK, BISI.JK, BABP.JK, FUTR.JK, PSKT.JK, OASA.JK, ASLI.JK, SSTM.JK, SIPD.JK, MGRO.JK, PORT.JK, DNAR.JK, MKAP.JK, BVIC.JK, BOLT.JK, PNGO.JK, IPCC.JK, BLTZ.JK, ASGR.JK, POLI.JK, DWGL.JK, BMTR.JK, GMTD.JK, WINS.JK, IFII.JK, MSJA.JK, BCAP.JK, OMRE.JK, BEEF.JK, KMTR.JK, NICE.JK, BKSW.JK, PRDA.JK, DOID.JK, TRUE.JK, BLUE.JK, MDIA.JK, WOOD.JK, ACST.JK, IMJS.JK, AMAG.JK, PTPP.JK, MTMH.JK, CSRA.JK, MLIA.JK, ITMA.JK, DGWG.JK, KETR.JK, NRCA.JK, DMMX.JK, SCCO.JK, INDR.JK, PNBS.JK, BRAM.JK, LUCY.JK, MBAP.JK, TPMA.JK, ELTY.JK, IPTV.JK, STRK.JK, TEBE.JK, ADHI.JK, LPGI.JK, SUNI.JK, HILL.JK, PSSI.JK, MINE.JK, FAST.JK, DVLA.JK, ERAL.JK, HERO.JK, KINO.JK, CSAP.JK, UCID.JK, IPCM.JK, MLPL.JK, VISI.JK, PTSN.JK, BBRM.JK, SPTO.JK, FMII.JK, PPRE.JK, MAIN.JK, AYAM.JK, EURO.JK, SKLT.JK, DEPO.JK, BSBK.JK, MKTR.JK, BMHS.JK, NEST.JK, PMJS.JK, BEKS.JK, KKGI.JK, DLTA.JK, AMFG.JK, RAAM.JK, TRGU.JK, ALDO.JK, GWSA.JK, PSAT.JK, GSMF.JK, CARS.JK, PADI.JK, BBLD.JK, DOOH.JK, ABDA.JK, BELL.JK, NETV.JK, MERK.JK, BLOG.JK, DILD.JK, TAMU.JK, CEKA.JK, ATIC.JK, TRST.JK, SONA.JK, BBSS.JK, KBLI.JK, BLES.JK, CFIN.JK, JKON.JK, TIFA.JK, CAMP.JK, RANC.JK, MITI.JK, TCID.JK, WSBP.JK, GZCO.JK, AISA.JK, CITY.JK, JIHD.JK, LTLS.JK, IBOS.JK, ADCP.JK, ARTA.JK, BUAH.JK, INDO.JK, WOMF.JK, BEST.JK, PANS.JK, TBMS.JK, ENAK.JK, RSCH.JK, BLTA.JK, JGLE.JK, MTWI.JK, ARII.JK, BTEK.JK, AREA.JK, BOLA.JK, SHID.JK, ZINC.JK, ASLC.JK, PEVE.JK, LIVE.JK, MMIX.JK, GHON.JK, CHIP.JK, WIRG.JK, GDST.JK, PBRX.JK, GRIA.JK, ATAP.JK, CMPP.JK, NELY.JK, RMKO.JK, NICK.JK, SMGA.JK, SPMA.JK, RELI.JK, HGII.JK, BUDI.JK, SKBM.JK, COCO.JK, LEAD.JK, VOKS.JK, PDPP.JK, MHKI.JK, NFCX.JK, PTPW.JK, PJAA.JK, ZATA.JK, NIKL.JK, FUJI.JK, AMOR.JK, PANR.JK, ADMG.JK, MGNA.JK, TALF.JK, AMAN.JK, BABY.JK, MTFN.JK, WTON.JK, IPOL.JK, SULI.JK, PMUI.JK, KSIX.JK, PADA.JK, LFLO.JK, BPFI.JK, JECC.JK, FORU.JK, HDFA.JK, KOKA.JK, BDKR.JK, DGIK.JK, WMUU.JK, PGJO.JK, RODA.JK, KDSI.JK, AXIO.JK, TIRA.JK, MDLN.JK, MOLI.JK, BEER.JK, HOKI.JK, BRNA.JK, GTBO.JK, BIKE.JK, UNIQ.JK, MPPA.JK, APEX.JK, AHAP.JK, GTRA.JK, SWID.JK, IKBI.JK, HOMI.JK, HOPE.JK, EKAD.JK, VIVA.JK, UNSP.JK, PEGE.JK, PZZA.JK, SOFA.JK, IRRA.JK, ELIT.JK, WEGE.JK, SOSS.JK, AWAN.JK, SMKL.JK, GLVA.JK, TRIS.JK, KOTA.JK, GUNA.JK, HAIS.JK, UNTD.JK, CHEK.JK, LABS.JK, BOAT.JK, PNSE.JK, MREI.JK, FITT.JK, KONI.JK, VTNY.JK, URBN.JK, TRON.JK, IDPR.JK, WINE.JK, DART.JK, PJHB.JK, GPRA.JK, MDKI.JK, KING.JK, CNKO.JK, UFOE.JK, BSML.JK, VERN.JK, HALO.JK, COAL.JK, APLI.JK, CRAB.JK, ESTA.JK, SURI.JK, MDRN.JK, MAXI.JK, KMDS.JK, CLPI.JK, BAYU.JK, VRNA.JK, TIRT.JK, IGAR.JK, LAPD.JK, IKPM.JK, SCNP.JK, MCAS.JK, REAL.JK, RIGS.JK, CCSI.JK, GDYR.JK, GULA.JK, NASA.JK, PDES.JK, CSIS.JK, GOLD.JK, PTPS.JK, CBPE.JK, SOLA.JK, TYRE.JK, ZONE.JK, BIPP.JK, BKDP.JK, ESTI.JK, IOTF.JK, LPLI.JK, VAST.JK, HYGN.JK, ASRM.JK, KREN.JK, SMLE.JK, DYAN.JK, DGNS.JK, EAST.JK, HAJJ.JK, TFAS.JK, SRSN.JK, JATI.JK, KBLM.JK, DADA.JK, BMSR.JK, KOBX.JK, NAIK.JK, KBAG.JK, TARA.JK, SATU.JK, ASPR.JK, ASHA.JK, YOII.JK, UVCR.JK, CRSN.JK, YPAS.JK, TRUS.JK, ATLA.JK, INTA.JK, ERTX.JK, GPSO.JK, PART.JK, MUTU.JK, SAFE.JK, KLAS.JK, AKPI.JK, ITIC.JK, CGAS.JK, EMDE.JK, MICE.JK, VINS.JK, ASMI.JK, HRME.JK, BPTR.JK, AMIN.JK, ASPI.JK, IKAI.JK, BINO.JK, SAGE.JK, TOSK.JK, BTON.JK, OKAS.JK, MPXL.JK, WGSH.JK, ACRO.JK, AGAR.JK, INOV.JK, POLA.JK, LMPI.JK, FIRE.JK, ANDI.JK, PUDP.JK, DOSS.JK, FWCT.JK, AKSI.JK, CASH.JK, KBLV.JK, PRIM.JK, NTBK.JK, DEWI.JK, OBAT.JK, ASJT.JK, ALKA.JK, ECII.JK, RELF.JK, LCKM.JK, PEHA.JK, AKKU.JK, ENZO.JK, AYLS.JK, INPS.JK, BAJA.JK, WINR.JK, ASDM.JK, SDPC.JK, TRJA.JK, SAPX.JK, WAPO.JK, PTMP.JK, BAUT.JK, MEJA.JK, JMAS.JK, LPPS.JK, OBMD.JK, NPGF.JK, NZIA.JK, MANG.JK, LION.JK, TAXI.JK, PTSP.JK, APII.JK, CAKK.JK, NANO.JK, SLIS.JK, DFAM.JK, WOWS.JK, SDMU.JK, CINT.JK, ZYRX.JK, DKHH.JK, MRAT.JK, ABBA.JK, BOBA.JK, DIVA.JK, PURA.JK, MARI.JK, PAMG.JK, BAPI.JK, CANI.JK, KOPI.JK, DSFI.JK, SMKM.JK, WEHA.JK, PURI.JK, LPIN.JK, IBFN.JK, RUIS.JK, NAYZ.JK, LAJU.JK, TRUK.JK, LAND.JK, KARW.JK, HELI.JK, CHEM.JK, SEMA.JK, PSDN.JK, IPAC.JK, SNLK.JK, INTD.JK, MSKY.JK, MBTO.JK, KRYA.JK, ASBI.JK, INCI.JK, TMPO.JK, GEMA.JK, ISAP.JK, YELO.JK, MERI.JK, PTIS.JK, ISEA.JK, FOOD.JK, LABA.JK, MPIX.JK, RGAS.JK, DEFI.JK, KUAS.JK, SBMA.JK, EPAC.JK, RCCC.JK, KIOS.JK, INAI.JK, RBMS.JK, MIRA.JK, NASI.JK, MEDS.JK, CSMI.JK, CTTH.JK, OLIV.JK, JAST.JK, IDEA.JK, OPMS.JK, PTDU.JK, PGLI.JK, FLMC.JK, BCIP.JK, INCF.JK, HDIT.JK, JAYA.JK, AIMS.JK, RUNS.JK, POLY.JK, OILS.JK, BATA.JK, KOIN.JK, ICON.JK, LRNA.JK, MPOW.JK, PICO.JK, IKAN.JK, TAYS.JK, ESIP.JK, KJEN.JK, LUCK.JK, TNCA.JK, KICI.JK, SOUL.JK, ARKA.JK, PLAN.JK, BMBL.JK, BAPA.JK, RICY.JK, WIDI.JK, DIGI.JK, INDX.JK, HADE.JK, TAMA.JK, PCAR.JK, LOPI.JK, GRPH.JK, HBAT.JK, PIPA.JK, KLIN.JK, PPRI.JK, AEGS.JK, SPRE.JK, KAQI.JK, NINE.JK, KOCI.JK, LMAX.JK, BRRC.JK, RAFI.JK, TOOL.JK, BATR.JK, AMMS.JK, KKES.JK, SICO.JK, BAIK.JK, GRPM.JK, KDTN.JK, MSIE.JK"
    tickers_input = st.text_area(
        "Masukkan kode saham (pisahkan dengan koma):", 
        default_tickers,
        height=100,
        key="input_tabel"
    )
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

    if st.button("Tampilkan Tabel"):
        if not tickers:
            st.warning("Silakan masukkan minimal satu kode saham.")
        else:
            with st.spinner("Mengambil data dari Yahoo Finance..."):
                end_date = datetime.today()
                start_date_12m = end_date - relativedelta(months=12)
                start_date_3m = end_date - relativedelta(months=3)
                
                data = []
                for ticker in tickers:
                    try:
                        stock = yf.Ticker(ticker)
                        hist = stock.history(start=start_date_12m.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
                        
                        if not hist.empty:
                            harga_sekarang = hist['Close'].iloc[-1]
                            first_date = hist.index[0].tz_localize(None) 
                            
                            if (first_date - start_date_12m).days > 14:
                                harga_12m, pct_12m = "-", "-"
                            else:
                                harga_12m = hist['Close'].iloc[0]
                                pct_12m = ((harga_sekarang - harga_12m) / harga_12m) * 100

                            tz = hist.index.tz
                            target_3m_ts = pd.Timestamp(start_date_3m.strftime('%Y-%m-%d'), tz=tz)
                            hist_3m = hist.loc[hist.index >= target_3m_ts]
                            
                            if not hist_3m.empty:
                                first_date_3m = hist_3m.index[0].tz_localize(None)
                                if (first_date_3m - start_date_3m).days > 14:
                                    harga_3m, pct_3m = "-", "-"
                                else:
                                    harga_3m = hist_3m['Close'].iloc[0]
                                    pct_3m = ((harga_sekarang - harga_3m) / harga_3m) * 100
                            else:
                                harga_3m, pct_3m = "-", "-"

                            data.append({
                                "Kode Saham": ticker,
                                "Harga Sekarang": round(harga_sekarang, 2),
                                "Harga 3 Bln Lalu": round(harga_3m, 2) if harga_3m != "-" else "-",
                                "Bedanya 3 Bln (%)": round(pct_3m, 2) if pct_3m != "-" else "-",
                                "Harga 12 Bln Lalu": round(harga_12m, 2) if harga_12m != "-" else "-",
                                "Bedanya 12 Bln (%)": round(pct_12m, 2) if pct_12m != "-" else "-"
                            })
                    except Exception as e:
                        continue
                
                if data:
                    df = pd.DataFrame(data)
                    def color_negative_positive(val):
                        if isinstance(val, (int, float)):
                            color = 'red' if val < 0 else 'green'
                            return f'color: {color}; font-weight: bold;'
                        return ''
                    st.dataframe(df.style.map(color_negative_positive, subset=['Bedanya 3 Bln (%)', 'Bedanya 12 Bln (%)']), use_container_width=True)
                else:
                    st.error("Tidak ada data yang ditemukan.")

# ==========================================
# TAB 2: GRAFIK SAHAM
# ==========================================
with tab2:
    st.write("Lihat pergerakan harga saham secara visual. Anda bisa memasukkan list saham menyamping (koma) atau ke bawah (enter).")
    
    # Pengaturan Range Waktu & Jenis Grafik dibagi ke 3 kolom
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        rentang_waktu = st.radio(
            "Pilih Rentang Waktu:",
            ("1 Hari", "5 Hari", "1 Bulan", "3 Bulan", "12 Bulan")
        )
    with col2:
        jenis_grafik = st.radio(
            "Pilih Jenis Grafik:",
            ("Line", "Candlestick")
        )
    
    range_mapping = {
        "1 Hari": ("1d", "5m"),
        "5 Hari": ("5d", "15m"),
        "1 Bulan": ("1mo", "1d"),
        "3 Bulan": ("3mo", "1d"),
        "12 Bulan": ("1y", "1d")
    }
    yf_period, yf_interval = range_mapping[rentang_waktu]

    with col3:
        contoh_input = "BEEF\nFOOD\nCARE\nPEGE\nNICL\nKRYA\nAKSI"
        grafik_input = st.text_area(
            "Masukkan List Saham:", 
            contoh_input,
            height=150,
            key="input_grafik"
        )
    
    if st.button("Tampilkan Grafik"):
        raw_tickers = grafik_input.replace('\n', ',').split(',')
        clean_tickers = []
        
        for t in raw_tickers:
            t = t.strip().upper()
            if t:
                if '.' not in t:
                    t += '.JK'
                if t not in clean_tickers:
                    clean_tickers.append(t)
                    
        if not clean_tickers:
            st.warning("Silakan masukkan minimal satu kode saham.")
        else:
            with st.spinner("Membuat grafik..."):
                for ticker in clean_tickers:
                    try:
                        stock = yf.Ticker(ticker)
                        hist = stock.history(period=yf_period, interval=yf_interval)
                        
                        if not hist.empty:
                            # Menentukan harga terendah dan tertinggi berdasarkan jenis grafik
                            if jenis_grafik == "Candlestick":
                                min_price = hist['Low'].min()
                                max_price = hist['High'].max()
                            else:
                                min_price = hist['Close'].min()
                                max_price = hist['Close'].max()
                                
                            # Menghitung padding (jarak atas dan bawah)
                            price_diff = max_price - min_price
                            if price_diff == 0: # Jika harga stagnan, beri sedikit margin manual
                                price_diff = min_price * 0.01 
                                
                            # Tambahkan jarak 10% dari selisih harga agar tidak menempel di garis
                            padding = price_diff * 0.1 
                            
                            fig = go.Figure()
                            
                            # Menentukan tipe plot yang digambar
                            if jenis_grafik == "Candlestick":
                                fig.add_trace(go.Candlestick(
                                    x=hist.index,
                                    open=hist['Open'],
                                    high=hist['High'],
                                    low=hist['Low'],
                                    close=hist['Close'],
                                    name=ticker
                                ))
                            else:
                                fig.add_trace(go.Scatter(
                                    x=hist.index,
                                    y=hist['Close'],
                                    mode='lines',
                                    name=ticker,
                                    line=dict(width=2)
                                ))
                            
                            # Mengatur layout
                            fig.update_layout(
                                title=f"<b>{ticker}</b> - Rentang: {rentang_waktu}",
                                yaxis_title="Harga (Rp)",
                                xaxis_title="Waktu",
                                height=350, # Ketinggian diturunkan agar lebih proporsional / melebar
                                margin=dict(l=40, r=40, t=50, b=20),
                                yaxis=dict(
                                    range=[min_price - padding, max_price + padding],
                                    autorange=False
                                ) 
                            )
                            
                            fig.update_xaxes(rangeslider_visible=False)
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning(f"Data tidak tersedia untuk {ticker} pada rentang waktu {rentang_waktu}.")
                    except Exception as e:
                        st.error(f"Terjadi kesalahan saat memuat grafik {ticker}.")
        rentang_waktu = st.radio(
            "Pilih Rentang Waktu:",
            ("1 Hari", "5 Hari", "1 Bulan", "3 Bulan", "12 Bulan")
        )
    
    # Mapping rentang waktu ke format yfinance (period, interval)
    # Catatan: Untuk 1 hari dan 5 hari, kita butuh interval intraday (menit/jam) agar grafik terbentuk
    range_mapping = {
        "1 Hari": ("1d", "5m"),
        "5 Hari": ("5d", "15m"),
        "1 Bulan": ("1mo", "1d"),
        "3 Bulan": ("3mo", "1d"),
        "12 Bulan": ("1y", "1d")
    }
    yf_period, yf_interval = range_mapping[rentang_waktu]

    with col2:
        # Input bisa di-enter (newline) atau koma, dengan/tanpa .JK
        contoh_input = "BEEF.JK\nFOOD\nCARE\nPEGE\nNICL\nKRYA\nAKSI"
        grafik_input = st.text_area(
            "Masukkan List Saham:", 
            contoh_input,
            height=150,
            key="input_grafik"
        )
    
    if st.button("Tampilkan Grafik"):
        # Membersihkan input (ubah enter jadi koma, lalu split)
        raw_tickers = grafik_input.replace('\n', ',').split(',')
        clean_tickers = []
        
        for t in raw_tickers:
            t = t.strip().upper()
            if t:
                # Otomatis tambahkan .JK jika tidak ada tanda titik (asumsi saham Indonesia)
                if '.' not in t:
                    t += '.JK'
                if t not in clean_tickers:
                    clean_tickers.append(t)
                    
        if not clean_tickers:
            st.warning("Silakan masukkan minimal satu kode saham.")
        else:
            with st.spinner("Membuat grafik..."):
                for ticker in clean_tickers:
                    try:
                        stock = yf.Ticker(ticker)
                        hist = stock.history(period=yf_period, interval=yf_interval)
                        
                        if not hist.empty:
                            # Mencari nilai terendah dan tertinggi untuk presisi Y-axis
                            min_price = hist['Low'].min()
                            max_price = hist['High'].max()
                            
                            # Membuat grafik Candlestick dengan Plotly
                            fig = go.Figure(data=[go.Candlestick(
                                x=hist.index,
                                open=hist['Open'],
                                high=hist['High'],
                                low=hist['Low'],
                                close=hist['Close'],
                                name=ticker
                            )])
                            
                            # Mengatur layout agar presisi
                            fig.update_layout(
                                title=f"<b>{ticker}</b> - Rentang: {rentang_waktu}",
                                yaxis_title="Harga (Rp)",
                                xaxis_title="Waktu",
                                height=500, # Tinggi grafik tetap konsisten
                                margin=dict(l=20, r=20, t=50, b=20),
                                # Mengunci Y-axis: bawah menyentuh min_price persis, atas diberi sedikit ruang
                                yaxis=dict(range=[min_price, max_price + (max_price - min_price) * 0.05]) 
                            )
                            
                            # Menghilangkan range slider di bawah grafik agar tampilan lebih bersih
                            fig.update_xaxes(rangeslider_visible=False)
                            
                            # Render grafik
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning(f"Data tidak tersedia untuk {ticker} pada rentang waktu {rentang_waktu}.")
                    except Exception as e:
                        st.error(f"Terjadi kesalahan saat memuat grafik {ticker}.")
