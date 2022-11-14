from bokeh.layouts import Column, gridplot, row, grid
from functools import partial
from bokeh.plotting import figure, output_file, show, ColumnDataSource, curdoc
from bokeh.models import HoverTool, CDSView, GroupFilter, NumericInput, Button
from bokeh.palettes import RdYlBu11 as palette
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from bokeh.models.widgets import Button, Div
import queries
# import telegramBot
from bokeh.resources import settings

settings.resources = 'inline'


def getRelatedSelections(eventID, selectionID=None):
    query = "SELECT DISTINCT MarketID, SelectionID, MarketName, SelectionName, Home, Away, LastTradedPrice  FROM viewEvents_GraphData WHERE EventID = ?"
    if selectionID:
        query = query + " AND SelectionID = '" + str(selectionID) + "'"
    query = query + ' ORDER BY MarketID'
    results = queries.getData(query, eventID)
    return results


def getTransactions(eventID, lastXminutes=0):
    query = "SELECT * FROM tblBFGraph_Data WHERE EventID = ? "
    if lastXminutes > 0:
        query = query + " AND (VolumeDate > DATEADD(mi,-" + str(
            lastXminutes) + ", (SELECT MAX(VolumeDate) FROM tblBFGraph_Data WHERE EventID =" + str(eventID) + "))) "
    # ORDER BY
    query = query + ' ORDER BY EventID, MarketID, SelectionID, VolumeDate'

    df_transactions = queries.getData(query, eventID, False, True)
    df_transactions['SelectionID'] = df_transactions['SelectionID'].astype(str)
    return df_transactions


def updateDatasource():
    bf_datasource.data = getTransactions(eventID, lastXminINPUT.value)
    return


def buttonCallBack(order, selectionID):
    data = getRelatedSelections(eventID, selectionID)

    if "BACK H" in order:
        btnMessage = "BACK " + str(data[0][4]) + " at " + str(data[0][6])
    elif "BACK A" in order:
        btnMessage = "BACK " + str(data[0][5]) + " at " + str(data[0][6])
    elif "BACK D" in order:
        btnMessage = "BACK DRAW at " + str(data[0][6])

    if "LAY H" in order:
        btnMessage = "LAY " + str(data[0][4]) + " at " + str(data[0][6])
    elif "LAY A" in order:
        btnMessage = "BACK " + str(data[0][5]) + " at " + str(data[0][6])
    elif "LAY D" in order:
        btnMessage = "LAY DRAW at " + str(data[0][6])
    url = "<a href='http://localhost:5006/bokehgraph?evID=" + str(eventID) + "'>Go To Graphs</a>"
    print(url)
    CHAT_ID = 1150468112
    # telegramBot.sendNotification("Trade Alert " + btnMessage, url, CHAT_ID)

    return


def renderGraphs(datasource, selectionID, selectionName, marketID, marketName):
    selectionView = CDSView(source=datasource, filters=[GroupFilter(column_name='SelectionID', group=str(selectionID)),
                                                        GroupFilter(column_name='MarketID', group=str(marketID))])

    # PRICE CHART
    g = figure(width=600, height=200, title=selectionName + " " + marketName)
    # g.sizing_mode ="scale_both"
    # SET HOVER FOR PRICE CHART
    my_hover = HoverTool()
    my_hover.tooltips = [('Price', '@Price{0.00}'), ('Volume', '@Volume{0.00 a}'),
                         ('VolumeDate', '@VolumeDate{%Y-%m-%d %H:%M:%S}')]
    my_hover.formatters = {'@VolumeDate': 'datetime'}
    g.add_tools(my_hover)
    g.step('index', 'Price', color='red', alpha=0.5, source=datasource, view=selectionView)
    # g.step('index','Price',color='red',alpha=0.5, source=datasource)

    # VOLUME CHART
    w = 1
    v = figure(width=600, height=200, title=selectionName + " " + marketName, x_range=g.x_range, x_axis_label=None)
    # v.sizing_mode ="scale_both"
    # SET HOVER FOR VOLUME CHART
    my_hover = HoverTool()
    my_hover.tooltips = [('Price', '@Price{0.00}'), ('Volume', '@Volume{0.00 a}'),
                         ('VolumeDate', '@VolumeDate{%Y-%m-%d %H:%M:%S}')]
    v.add_tools(my_hover)
    v.vbar('index', w, 'Volume', source=datasource, view=selectionView)
    # v.vbar('index',w,'Volume',source=datasource)

    # LAY BUTTON
    btnLabel = "LAY " + str(selectionName) + " " + str(marketName)
    buttonLay = Button(label=btnLabel, name=btnLabel, background="#FFC0CB")
    buttonLay.on_click(partial(buttonCallBack, order=btnLabel, selectionID=selectionID))

    # BACK BUTTON
    btnLabel = "BACK " + str(selectionName) + " " + str(marketName)
    buttonBack = Button(label=btnLabel, name=btnLabel, button_type='primary')
    buttonBack.on_click(partial(buttonCallBack, order=btnLabel, selectionID=selectionID))

    # buttonColumn = Column(buttonLay,buttonBack,sizing_mode="scale_both")

    # column = Column(buttonColumn,g,v,sizing_mode="scale_both")
    column = Column(buttonLay, buttonBack, g, v, sizing_mode="scale_both")

    return column


# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# We can request all graphs that belong to an EVENT.
# We can request CUSTOM selections

arguments = curdoc().session_context.request.arguments
# graphType = str(arguments.get('graphType')[0],'utf-8')
eventID = str(arguments.get('evID')[0], 'utf-8')

# SET DATASOURCE FOR ALL
bf_datasource = ColumnDataSource(getTransactions(eventID))

# FOR EACH SELECTION, MAKE A GRAPH
selections = getRelatedSelections(eventID)
title = str(selections[0][4]) + ' vs ' + str(selections[0][5])
curdoc().title = title

listofGraphs = []
for selection in selections:
    graphs = renderGraphs(bf_datasource, selection[1], selection[3], selection[0], selection[2])
    listofGraphs.append(graphs)

r = row(children=listofGraphs, sizing_mode='stretch_both')
lastXminINPUT = NumericInput(value=0, title="Last X Minutes")
# div = Div(text='<div height="120px" width="700px" overflow="hidden" float="left" overflow="auto"> <iframe height="200px" width="100%" border="none" src="https://www.sofascore.com/event/10388461/attack-momentum/embed"></iframe></div>')
# curdoc().add_root(div)
curdoc().add_root(lastXminINPUT)
curdoc().add_root(r)

curdoc().add_periodic_callback(updateDatasource, 5000)
