#Display Dropdown for Sports, 
#Display Dropdown showing Events,Betfair, Sofascore
#IF Betfair, Dropdown for Markets/Selections
import pandas as pd
import webbrowser
from datetime import datetime
from queries import getData
from dash import  Dash, dash_table, dcc, html, State
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

PRINT = False
REFRESH_PER_SECOND = 30

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#DATA FUNCTIONS 

def getMarkets(sport):
    query ="SELECT DISTINCT MarketName FROM tblBetfairSelections"
    
    if sport != 'All':
        query = query + " WHERE Sport = '" + sport + "'"
    orderby = ' ORDER BY MarketName'
    query = query + orderby
    queryResult = getData(query,asDataFrame=True)          
    if PRINT: print(queryResult)
    return queryResult

def getDataBy_Market(sport,isLive):
    query ="SELECT DISTINCT EventID, Sport, Home, Away, MarketID, MarketName FROM tblBetfairSelections WHERE EventID IS NOT NULL "
    
    if sport != 'All':
        query = query + " WHERE Sport = '" + sport + "'"

    if isLive == "Live":
        query = query + " AND Live = 1"
    elif isLive == "PreGame":
        query = query + " AND Live = 0"
    
    orderby = ' ORDER BY Sport, EventID,MarketID'
    query = query + orderby
    queryResult = getData(query,asDataFrame=True)          
    if PRINT: print(queryResult)

    return queryResult

def getDataBy_Selections(sport,isLive):
    query ="SELECT DISTINCT EventID, Sport, Home, Away, MarketID, MarketName, SelectionID, SelectionName, LastTradedPrice FROM tblBetfairSelections WHERE EventID IS NOT NULL "
    
    if sport != 'All':
        query = query + " AND Sport = '" + sport + "'"

    if isLive == "Live":
        query = query + " AND Live = 1"
    elif isLive == "PreGame":
        query = query + " AND Live = 0"

    orderby = ' ORDER BY Sport, EventID,MarketID, SelectionName'
    query = query + orderby
    queryResult = getData(query,asDataFrame=True)          
    if PRINT: print(queryResult)

    return queryResult

def getDataBy_SofaEvents(sport):
    query ="SELECT *, 'http://161.97.91.91:5006/bokehgraph?evID=' AS URL FROM viewEvents WHERE Sport IS NOT NULL"    
    if sport != 'All':
        query = query + " AND Sport = '" + sport + "'"

    #if isLive == "Live":
    #    query = query + " AND Live = 1"
    #elif isLive == "PreGame":
    #    query = query + " AND Live = 0"
    
    orderby = ' ORDER BY MatchPeriod, Timer, Tournament, Sport, Home'
    query = query + orderby
    queryResult = getData(query,asDataFrame=True)          
    if PRINT: print(queryResult)
    return queryResult

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#LAYOUT INFORMATION

app = Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])

def table_type(df_column):  
    if isinstance(df_column.dtype, pd.DatetimeTZDtype):
        return 'datetime',
    elif (isinstance(df_column.dtype, pd.StringDtype) or
            isinstance(df_column.dtype, pd.BooleanDtype) or
            isinstance(df_column.dtype, pd.CategoricalDtype) or
            isinstance(df_column.dtype, pd.PeriodDtype)):
        return 'text'
    elif (isinstance(df_column.dtype, pd.SparseDtype) or
            isinstance(df_column.dtype, pd.IntervalDtype) or
            isinstance(df_column.dtype, pd.Int8Dtype) or
            isinstance(df_column.dtype, pd.Int16Dtype) or
            isinstance(df_column.dtype, pd.Int32Dtype) or
            isinstance(df_column.dtype, pd.Int64Dtype)):
        return 'numeric'
    else:
        return 'any'

def tablePresentation(df_column):
    if 'Home': return 'markdown'
    return

def convertToLink(val):
    #return '<a target="_blank" href="{}">{}</a>'.format(val, val)
    #return "[{0}](https://www.google.com/search?q={0})".format(val[""])
    event = str(val.EventID)
    if event == 'nan':
        return ""
    else:
        event = event.replace(".0","")    
    
    return "[{0}](http://161.97.91.91:5006/bokehgraph?evID={1})".format("Graphs",event)

df_Selections = getDataBy_SofaEvents('All')
#df_Selections.style.format({'URL':convertToLink})
df_Selections["URL"] = df_Selections.apply(convertToLink,axis=1)


app.layout =html.Div(children=[
            
            dbc.Alert(id='lastupdate',color="dark"),
            html.Div(children=[
                dbc.Button("Open Graphs", color="secondary", className="me-1", id="toGraphPage", target="_blank"),
                dbc.Button("Pairing System", color="secondary", className="me-1", id="toPairPage", target="_blank")
            ]),
            
            html.Br(),

            dash_table.DataTable(
            id = "MainTable",
            data = df_Selections.to_dict('records'),
            #columns= [{"name": i, "id": i,'type': table_type(df_Selections[i])} for i in df_Selections.columns],
            columns= [{'id': x, 'name': x, 'type': 'text', 'presentation': 'markdown'} if (x == 'URL')
                        else {'id': x, 'name': x, 'type': table_type(df_Selections[x])} for x in df_Selections.columns],
            #markdown_options ={'html':True},
            page_action='none',
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            row_selectable="multi",
            selected_rows=[],
            style_table={'height': '800px', 'overflowY': 'auto','overflowX': 'auto'},
            fixed_rows={'headers': True},
            style_data={'whiteSpace': 'normal','height': 'auto'},
            style_cell={'textAlign': 'center'},
            style_header={'backgroundColor': 'rgb(50, 50, 50)','fontWeight': 'bold', 'color':'white'},
            tooltip_header={'H_S': 'Home Team/Player Goals or Sets Won','A_S': 'Away Team/Player Goals or Sets Won'},
            tooltip_delay=0,
            tooltip_duration=None,
            style_cell_conditional=[
            {'if': {'column_id': 'EventID'},'width': '120px'},
            #{'if': {'column_id': 'SofaID'},'width': '4%'},
            {'if': {'column_id': 'Timer'},'width': '80px'},
            #{'if': {'column_id': 'Sport'},'width': '4%'},
            #{'if': {'column_id': 'Tournament'},'width': '13%'},
            #{'if': {'column_id': 'MatchPeriod'},'width': '10%'},
            #{'if': {'column_id': 'League'},'width': '10%'},
            #{'if': {'column_id': 'Home'},'width': '10%'},
            #{'if': {'column_id': 'Away'},'width': '10%'},            
            #{'if': {'column_id': 'Sport'},'width': '10%'},
            #{'if': {'column_id': 'MarketID'},'width': '10%'},
            {'if': {'column_id': 'H_S'},'width': '60px'},
            {'if': {'column_id': 'A_S'},'width': '60px'},
            {'if': {'column_id': '1'},'width': '60px'},
            {'if': {'column_id': 'X'},'width': '60px'},
            {'if': {'column_id': '2'},'width': '60x'},            
            #{'if': {'column_id': 'EventID',},'display': 'None',},
            {'if': {'column_id': 'SofaID',},'display': 'None',},
            #{'if': {'column_id': 'URL',},'display': 'None',}
            ]
            ),            
            dcc.Interval(
                id='interval-component',
                interval=REFRESH_PER_SECOND*1000, # in milliseconds
                n_intervals=0, disabled=False, max_intervals=-1
            ),
            html.Br()            
            
            ])
            #

# Display data in table every second
@app.callback(
    Output('lastupdate', 'children'),
    Output('MainTable', 'data'),
    Input('interval-component', 'n_intervals'))
def UpdateDashBoard(n):
    df_Selections = getDataBy_SofaEvents('All')   
    df_Selections["URL"] = df_Selections.apply(convertToLink,axis=1)     
    lastUpdate = "Last Update: " + str(datetime.now().strftime('%H:%M:%S'))
    htmlcontainer = html.P(lastUpdate, className="alert-heading"),html.Hr()
    return htmlcontainer, df_Selections.to_dict('records')

#@app.callback(    
#    Output('toGraphPage', 'href'),
#    Input('toGraphPage', 'n_clicks'))
#def UpdateDashBoard(n):
#    if n:
#        if derived_virtual_selected_rows is None:
#            derived_virtual_selected_rows = []
#            dff = df if rows is None else pd.DataFrame(rows)

#url = "https://www.google.com/search?q=event"
#    else:
#        url=""
#    return url

@app.callback(
    Output('toGraphPage', 'href'),
    Input('MainTable', "derived_virtual_data"),
    Input('MainTable', "derived_virtual_selected_rows"))
def update_graphs(rows, selected_rows):
    # When the table is first rendered, `derived_virtual_data` and
    # `derived_virtual_selected_rows` will be `None`. This is due to an
    # idiosyncrasy in Dash (unsupplied properties are always None and Dash
    # calls the dependent callbacks when the component is first rendered).
    # So, if `rows` is `None`, then the component was just rendered
    # and its value will be the same as the component's dataframe.
    # Instead of setting `None` in here, you could also set
    # `derived_virtual_data=df.to_rows('dict')` when you initialize
    # the component.
    if selected_rows is None:
        selected_rows = []
        return ""
    

    df_actualData = df_Selections if rows is None else pd.DataFrame(rows)
    #print(selected_rows)
    if len(selected_rows) == 0: return ""
    df_FilteredData = df_actualData.iloc[selected_rows]
    print(df_FilteredData)
    #df_FilteredData = df_actualData.loc(df_actualData.index.isin(selected_rows))
    #print(df_FilteredData)


    #dff = selected_rows_ids if rows is None else pd.DataFrame(rows)    
    #print(dff)
    params = ""
    for index,df_selRow in df_FilteredData.iterrows():        
        params = params + df_selRow["Home"] + "?"
    return "http://www.google.com/search?q="+params


if __name__ == '__main__':    
    app.run_server(host='0.0.0.0',debug=True)
    


