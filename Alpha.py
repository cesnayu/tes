import streamlit as st
import yfinance as yf
import pandas as pd

# Konfigurasi Tampilan
st.set_page_config(page_title="Day Trading Scanner", layout="wide")

st.title("📈 Day Trading Volatility Scanner")
st.markdown("---")

# Sidebar untuk Input List Saham dan Parameter
with st.sidebar:
    st.header("Konfigurasi Scanner")
    
    # EDIT BAGIAN INI: Daftar saham default Anda
    default_tickers = "BREN.jk, BBCA.jk, DSSA.jk, BBRI.jk, TPIA.jk, DCII.jk, BYAN.jk, AMMN.jk, BMRI.jk, TLKM.jk, ASII.jk, MORA.jk, SRAJ.jk, CUAN.jk, BRPT.jk, BBNI.jk, PANI.jk, BNLI.jk, BRMS.jk, CDIA.jk, DNET.jk, IMPC.jk, FILM.jk, MPRO.jk, BRIS.jk, ICBP.jk, HMSP.jk, BUMI.jk, EMAS.jk, UNTR.jk, ANTM.jk, NCKL.jk, SMMA.jk, ADMR.jk, CASA.jk, UNVR.jk, RISE.jk, CPIN.jk, MLPT.jk, AMRT.jk, MDKA.jk, ISAT.jk, MBMA.jk, GOTO.jk, INCO.jk, AADI.jk, INDF.jk, PTRO.jk, BELI.jk, ADRO.jk, EXCL.jk, TCPI.jk, KLBF.jk, EMTK.jk, MYOR.jk, PGAS.jk, INKP.jk, PGUN.jk, PGEO.jk, GEMS.jk, MTEL.jk, BNGA.jk, CMRY.jk, ARCI.jk, TBIG.jk, MEGA.jk, SILO.jk, MEDC.jk, GIAA.jk, SOHO.jk, VKTR.jk, CBDK.jk, MIKA.jk, NISP.jk, JPFA.jk, GGRM.jk, TOWR.jk, BBHI.jk, ENRG.jk, TAPG.jk, SUPA.jk, BUVA.jk, PTBA.jk, BINA.jk, COIN.jk, AVIA.jk, JSMR.jk, AKRA.jk, NSSS.jk, PNBN.jk, ITMG.jk, BDMN.jk, ARKO.jk, MDIY.jk, TINS.jk, BSIM.jk, INTP.jk, JARR.jk, BKSL.jk, BTPN.jk, ARTO.jk, FAPA.jk, MKPI.jk, RMKE.jk, SRTG.jk, TKIM.jk, MAPA.jk, MSIN.jk, MAPI.jk, RLCO.jk, HEAL.jk, BSDE.jk, KPIG.jk, CITA.jk, PWON.jk, BNBR.jk, APIC.jk, BBTN.jk, SMGR.jk, RAJA.jk, POLU.jk, LIFE.jk, BNII.jk, INDY.jk, CTRA.jk, SMAR.jk, SCMA.jk, SSMS.jk, CARE.jk, ULTJ.jk, SIDO.jk, DSNG.jk, BBSI.jk, BUKA.jk, AALI.jk, RATU.jk, BBKP.jk, HRUM.jk, CMNT.jk, SGRO.jk, PSAB.jk, JRPT.jk, YUPI.jk, STAA.jk, STTP.jk, GOOD.jk, MCOL.jk, WIFI.jk, AUTO.jk, TSPC.jk, NICL.jk, ALII.jk, SHIP.jk, MLBI.jk, PACK.jk, DEWA.jk, CYBR.jk, PRAY.jk, POWR.jk, ESSA.jk, BMAS.jk, MIDI.jk, EDGE.jk, BIPI.jk, BSSR.jk, SMSM.jk, ADMF.jk, ELPI.jk, BFIN.jk, HRTA.jk, CLEO.jk, BTPS.jk, CMNP.jk, CNMA.jk, BANK.jk, ADES.jk, INPP.jk, BJBR.jk, SIMP.jk, BJTM.jk, PNLF.jk, INET.jk, SINI.jk, TLDN.jk, GMFI.jk, NATO.jk, BBMD.jk, LSIP.jk, TMAS.jk, ABMM.jk, DUTI.jk, BHAT.jk, DAAZ.jk, SGER.jk, DMND.jk, CLAY.jk, IBST.jk, MTDL.jk, BULL.jk, ACES.jk, LPKR.jk, DMAS.jk, SMRA.jk, SSIA.jk, ERAA.jk, EPMT.jk, SMDR.jk, KRAS.jk, JSPT.jk, BOGA.jk, MAYA.jk, AGII.jk, OMED.jk, PALM.jk, ANJT.jk, TOBA.jk, DATA.jk, BESS.jk, INDS.jk, CASS.jk, ELSA.jk, AGRO.jk, SAME.jk, UANG.jk, MNCN.jk, LINK.jk, BPII.jk, YULE.jk, TRIN.jk, BALI.jk, UDNG.jk, PBSA.jk, CTBN.jk, DRMA.jk, NIRO.jk, DKFT.jk, GTSI.jk, MTLA.jk, BBYB.jk, TFCO.jk, ROTI.jk, FISH.jk, TRIM.jk, PYFA.jk, TGKA.jk, GOLF.jk, KIJA.jk, JTPE.jk, MASB.jk, HUMI.jk, FORE.jk, MPMX.jk, RDTX.jk, MSTI.jk, BSWD.jk, IMAS.jk, BIRD.jk, LPCK.jk, ASSA.jk, TUGU.jk, BWPT.jk, WIIM.jk, RONY.jk, LPPF.jk, CENT.jk, SDRA.jk, SURE.jk, VICI.jk, MGLV.jk, NOBU.jk, KEEN.jk, PSGO.jk, AMAR.jk, CPRO.jk, CBRE.jk, SOCI.jk, ARNA.jk, TBLA.jk, STAR.jk, GJTL.jk, VICO.jk, PBID.jk, INPC.jk, GGRP.jk, IRSX.jk, AGRS.jk, HEXA.jk, TOTL.jk, UNIC.jk, SMMT.jk, BUKK.jk, ROCK.jk, SKRN.jk, MDLA.jk, MMLP.jk, MINA.jk, BACA.jk, MAPB.jk, KEJU.jk, BGTG.jk, SOTS.jk, MBSS.jk, SAMF.jk, BHIT.jk, ARGO.jk, CBUT.jk, PNIN.jk, MARK.jk, SMDM.jk, ISSP.jk, FPNI.jk, APLN.jk, MYOH.jk, ASRI.jk, SMIL.jk, DAYA.jk, KAEF.jk, IFSH.jk, BNBA.jk, RALS.jk, JAWA.jk, MCOR.jk, PKPK.jk, HATM.jk, TOTO.jk, BCIC.jk, IATA.jk, MAHA.jk, FOLK.jk, SMBR.jk, SFAN.jk, BISI.jk, BABP.jk, FUTR.jk, PSKT.jk, OASA.jk, ASLI.jk, SSTM.jk, SIPD.jk, MGRO.jk, PORT.jk, DNAR.jk, MKAP.jk, BVIC.jk, BOLT.jk, PNGO.jk, IPCC.jk, BLTZ.jk, ASGR.jk, POLI.jk, DWGL.jk, BMTR.jk, GMTD.jk, WINS.jk, IFII.jk, MSJA.jk, BCAP.jk, OMRE.jk, BEEF.jk, KMTR.jk, NICE.jk, BKSW.jk, PRDA.jk, DOID.jk, TRUE.jk, BLUE.jk, MDIA.jk, WOOD.jk, ACST.jk, IMJS.jk, AMAG.jk, PTPP.jk, MTMH.jk, CSRA.jk, MLIA.jk, ITMA.jk, DGWG.jk, KETR.jk, NRCA.jk, DMMX.jk, SCCO.jk, INDR.jk, PNBS.jk, BRAM.jk, LUCY.jk, MBAP.jk, TPMA.jk, ELTY.jk, IPTV.jk, STRK.jk, TEBE.jk, ADHI.jk, LPGI.jk, SUNI.jk, HILL.jk, PSSI.jk, MINE.jk, FAST.jk, DVLA.jk, ERAL.jk, HERO.jk, KINO.jk, CSAP.jk, UCID.jk, IPCM.jk, MLPL.jk, VISI.jk, PTSN.jk, BBRM.jk, SPTO.jk, FMII.jk, PPRE.jk, MAIN.jk, AYAM.jk, EURO.jk, SKLT.jk, DEPO.jk, BSBK.jk, MKTR.jk, BMHS.jk, NEST.jk, PMJS.jk, BEKS.jk, KKGI.jk, DLTA.jk, AMFG.jk, RAAM.jk, TRGU.jk, ALDO.jk, GWSA.jk, PSAT.jk, GSMF.jk, CARS.jk, PADI.jk, BBLD.jk, DOOH.jk, ABDA.jk, BELL.jk, NETV.jk, MERK.jk, BLOG.jk, DILD.jk, TAMU.jk, CEKA.jk, ATIC.jk, TRST.jk, SONA.jk, BBSS.jk, KBLI.jk, BLES.jk, CFIN.jk, JKON.jk, TIFA.jk, CAMP.jk, RANC.jk, MITI.jk, TCID.jk, WSBP.jk, GZCO.jk, AISA.jk, CITY.jk, JIHD.jk, LTLS.jk, IBOS.jk, ADCP.jk, ARTA.jk, BUAH.jk, INDO.jk, WOMF.jk, BEST.jk, PANS.jk, TBMS.jk, ENAK.jk, RSCH.jk, BLTA.jk, JGLE.jk, MTWI.jk, ARII.jk, BTEK.jk, AREA.jk, BOLA.jk, SHID.jk, ZINC.jk, ASLC.jk, PEVE.jk, LIVE.jk, MMIX.jk, GHON.jk, CHIP.jk, WIRG.jk, GDST.jk, PBRX.jk, GRIA.jk, ATAP.jk, CMPP.jk, NELY.jk, RMKO.jk, NICK.jk, SMGA.jk, SPMA.jk, RELI.jk, HGII.jk, BUDI.jk, SKBM.jk, COCO.jk, LEAD.jk, VOKS.jk, PDPP.jk, MHKI.jk, NFCX.jk, PTPW.jk, PJAA.jk, ZATA.jk, NIKL.jk, FUJI.jk, AMOR.jk, PANR.jk, ADMG.jk, MGNA.jk, TALF.jk, AMAN.jk, BABY.jk, MTFN.jk, WTON.jk, IPOL.jk, SULI.jk, PMUI.jk, KSIX.jk, PADA.jk, LFLO.jk, BPFI.jk, JECC.jk, FORU.jk, HDFA.jk, KOKA.jk, BDKR.jk, DGIK.jk, WMUU.jk, PGJO.jk, RODA.jk, KDSI.jk, AXIO.jk, TIRA.jk, MDLN.jk, MOLI.jk, BEER.jk, HOKI.jk, BRNA.jk, GTBO.jk, BIKE.jk, UNIQ.jk, MPPA.jk, APEX.jk, AHAP.jk, GTRA.jk, SWID.jk, IKBI.jk, HOMI.jk, HOPE.jk, EKAD.jk, VIVA.jk, UNSP.jk, PEGE.jk, PZZA.jk, SOFA.jk, IRRA.jk, ELIT.jk, WEGE.jk, SOSS.jk, AWAN.jk, SMKL.jk, GLVA.jk, TRIS.jk, KOTA.jk, GUNA.jk, HAIS.jk, UNTD.jk, CHEK.jk, LABS.jk, BOAT.jk, PNSE.jk, MREI.jk, FITT.jk, KONI.jk, VTNY.jk, URBN.jk, TRON.jk, IDPR.jk, WINE.jk, DART.jk, PJHB.jk, GPRA.jk, MDKI.jk, KING.jk, CNKO.jk, UFOE.jk, BSML.jk, VERN.jk, HALO.jk, COAL.jk, APLI.jk, CRAB.jk, ESTA.jk, SURI.jk, MDRN.jk, MAXI.jk, KMDS.jk, CLPI.jk, BAYU.jk, VRNA.jk, TIRT.jk, IGAR.jk, LAPD.jk, IKPM.jk, SCNP.jk, MCAS.jk, REAL.jk, RIGS.jk, CCSI.jk, GDYR.jk, GULA.jk, NASA.jk, PDES.jk, CSIS.jk, GOLD.jk, PTPS.jk, CBPE.jk, SOLA.jk, TYRE.jk, ZONE.jk, BIPP.jk, BKDP.jk, ESTI.jk, IOTF.jk, LPLI.jk, VAST.jk, HYGN.jk, ASRM.jk, KREN.jk, SMLE.jk, DYAN.jk, DGNS.jk, EAST.jk, HAJJ.jk, TFAS.jk, SRSN.jk, JATI.jk, KBLM.jk, DADA.jk, BMSR.jk, KOBX.jk, NAIK.jk, KBAG.jk, TARA.jk, SATU.jk, ASPR.jk, ASHA.jk, YOII.jk, UVCR.jk, CRSN.jk, YPAS.jk, TRUS.jk, ATLA.jk, INTA.jk, ERTX.jk, GPSO.jk, PART.jk, MUTU.jk, SAFE.jk, KLAS.jk, AKPI.jk, ITIC.jk, CGAS.jk, EMDE.jk, MICE.jk, VINS.jk, ASMI.jk, HRME.jk, BPTR.jk, AMIN.jk, ASPI.jk, IKAI.jk, BINO.jk, SAGE.jk, TOSK.jk, BTON.jk, OKAS.jk, MPXL.jk, WGSH.jk, ACRO.jk, AGAR.jk, INOV.jk, POLA.jk, LMPI.jk, FIRE.jk, ANDI.jk, PUDP.jk, DOSS.jk, FWCT.jk, AKSI.jk, CASH.jk, KBLV.jk, PRIM.jk, NTBK.jk, DEWI.jk, OBAT.jk, ASJT.jk, ALKA.jk, ECII.jk, RELF.jk, LCKM.jk, PEHA.jk, AKKU.jk, ENZO.jk, AYLS.jk, INPS.jk, BAJA.jk, WINR.jk, ASDM.jk, SDPC.jk, TRJA.jk, SAPX.jk, WAPO.jk, PTMP.jk, BAUT.jk, MEJA.jk, JMAS.jk, LPPS.jk, OBMD.jk, NPGF.jk, NZIA.jk, MANG.jk, LION.jk, TAXI.jk, PTSP.jk, APII.jk, CAKK.jk, NANO.jk, SLIS.jk, DFAM.jk, WOWS.jk, SDMU.jk, CINT.jk, ZYRX.jk, DKHH.jk, MRAT.jk, ABBA.jk, BOBA.jk, DIVA.jk, PURA.jk, MARI.jk, PAMG.jk, BAPI.jk, CANI.jk, KOPI.jk, DSFI.jk, SMKM.jk, WEHA.jk, PURI.jk, LPIN.jk, IBFN.jk, RUIS.jk, NAYZ.jk, LAJU.jk, TRUK.jk, LAND.jk, KARW.jk, HELI.jk, CHEM.jk, SEMA.jk, PSDN.jk, IPAC.jk, SNLK.jk, INTD.jk, MSKY.jk, MBTO.jk, KRYA.jk, ASBI.jk, INCI.jk, TMPO.jk, GEMA.jk, ISAP.jk, YELO.jk, MERI.jk, PTIS.jk, ISEA.jk, FOOD.jk, LABA.jk, MPIX.jk, RGAS.jk, DEFI.jk, KUAS.jk, SBMA"
    
    input_saham = st.text_area(
        "List Saham (pisahkan dengan koma):", 
        value=default_tickers,
        help="Gunakan format .JK untuk saham Indonesia"
    )
    
    threshold = st.slider("Target Volatilitas H-L (%)", 1.0, 10.0, 3.0)
    
    st.info("Scanner ini membandingkan High vs Low di hari yang sama untuk melihat ruang gerak harga.")

# Fungsi Data Processing
def get_data(tickers_str, threshold):
    # Membersihkan input dari spasi dan memecah string menjadi list
    tickers = [t.strip().upper() for t in tickers_str.split(",") if t.strip()]
    final_data = []
    
    progress_bar = st.progress(0)
    for idx, ticker in enumerate(tickers):
        try:
            # Ambil data 10 hari (interval harian)
            data = yf.download(ticker, period="10d", interval="1d", progress=False)
            if len(data) < 5: continue
                
            last_5 = data.tail(5).copy()
            
            # Rumus Intraday Range: ((High - Low) / Low) * 100
            last_5['HL_Pct'] = (last_5['High'] - last_5['Low']) / last_5['Low'] * 100
            
            dates = last_5.index.strftime('%d/%m').tolist()
            ranges = last_5['HL_Pct'].tolist()
            count_met = (last_5['HL_Pct'] >= threshold).sum()
            
            row = {'Ticker': ticker}
            for i in range(5):
                row[dates[i]] = round(ranges[i], 2)
            
            row['Freq'] = count_met
            final_data.append(row)
        except:
            st.warning(f"Gagal menarik data untuk: {ticker}")
        
        # Update Progress Bar
        progress_bar.progress((idx + 1) / len(tickers))
            
    return pd.DataFrame(final_data)

# Tampilan Utama
df = get_data(input_saham, threshold)

if not df.empty:
    # Mengurutkan berdasarkan tanggal terbaru (kolom sebelum terakhir)
    kolom_terbaru = df.columns[-2]
    df_sorted = df.sort_values(by=kolom_terbaru, ascending=False)
    
    # Fungsi styling warna sel
    def highlight_volatility(val):
        if isinstance(val, (int, float)) and val >= threshold:
            return 'background-color: #1e4d2b; color: #a2ffb8; font-weight: bold'
        return ''

    st.subheader(f"Dashboard Volatilitas (Data Terakhir: {kolom_terbaru})")
    
    # Menampilkan tabel interaktif
    st.dataframe(
        df_sorted.style.applymap(highlight_volatility, subset=df_sorted.columns[1:-1]),
        use_container_width=True,
        height=450
    )
    
    st.caption(f"Keterangan: Sel berwarna hijau menandakan volatilitas hari tersebut >= {threshold}%")
else:
    st.warning("Silakan masukkan list saham di sidebar dan pastikan koneksi internet aktif.")

