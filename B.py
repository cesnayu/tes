    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_accurate_data, t): t for t in tickers}
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            if res: results.append(res)

    if results:
        df = pd.DataFrame(results)
        
        # Filtering berdasarkan input user
        final_df = df[
            (df['Value (IDR)'] >= target_val) & 
            (df['Vol (Lot)'] >= target_lot)
        ].sort_values(by="Return (%)", ascending=False)

        st.dataframe(final_df.style.format({
            "Price": "{:,.0f}",
            "Prev": "{:,.0f}",
            "Value (IDR)": "{:,.0f}",
            "Vol (Lot)": "{:,.0f}"
        }))
        
        gc.collect()
