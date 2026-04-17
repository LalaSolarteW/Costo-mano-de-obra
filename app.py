import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output
from graficas import figimpactoservicio, figboxplot, ahorro_total_fmt, balance_total_fmt, perdida_total_fmt, figboxtotal, fig_dif, fig_total, figcomercial, fig_ahorro, fig_volumen, fig_valor, fig_cat_ahorro
from graficas import fig_confe, fig, fig_subl, fig_sub, fig_bord, fig_bordado, fig_estampado, fig_est,  fig_pqt_sin,  fig_pqt_sinM, fig_pre, fig_prelavado, fig_cyc, fig_cycc, fig_pqt_com, fig_pqtcom, fig_valor_pro, fig,fig_vol
from dash.exceptions import PreventUpdate
app = Dash(__name__)
server = app.server

# Importamos el excel con el df que necesitamos para graficar
df_costos_fechacom = pd.read_excel('dffinn.xlsx')

# Nos aseguramos de tener la columna en formato de fecha
df_costos_fechacom["Fecha"] = pd.to_datetime(df_costos_fechacom["Fecha"])
df_costos_fechacom = df_costos_fechacom[df_costos_fechacom["Fecha"].dt.year >= 2024]
# Creamos distintas columnas para facilitar la creación del gráfico
df_costos_fechacom["Año"] = df_costos_fechacom["Fecha"].dt.year
df_costos_fechacom["Mes"] = df_costos_fechacom["Fecha"].dt.month
df_costos_fechacom["Mes_nombre"] = df_costos_fechacom["Fecha"].dt.strftime("%b")
df_costos_fechacom["Año-Mes"] = df_costos_fechacom["Fecha"].dt.to_period("M").astype(str)
fechas_unicas = sorted(df_costos_fechacom["Año-Mes"].unique())


# HISTORICO DE PRECIOS POR CATEGORÍA

# Creamos el filtro de cliente
dcc.Dropdown(
    options=[
        {"label": c, "value": c} 
        for c in df_costos_fechacom["Cliente"].unique()
        ],
    multi=True,
    placeholder= "Selecciona el cliente",
    id="filtro-cliente"
)

# Creamos el filtro de categoría
dcc.Dropdown(
    options=[
        {"label": c, "value":c}
        for c in df_costos_fechacom["Categoría"].unique()
    ],
    multi=True,
    placeholder="Seleccione la categoría",
    id="filtro-categoria"
)

#creamos el slider para las fechas
dcc.RangeSlider(
    min=0,
    max=len(fechas_unicas) -1,
    value=[0, len(fechas_unicas) - 1],
    marks=None,
    id="filtro-fecha"
)

@app.callback(
    Output("grafico-historico", "figure"),
    Input("filtro-cliente", "value"),
    Input("filtro-categoria", "value"),
    Input("filtro-fecha", "value")
)
def actualizar(cliente, categoria, rango_fechas):

    df_filtrado = df_costos_fechacom.copy()

    # Filtro cliente
    if cliente:
        df_filtrado = df_filtrado[df_filtrado["Cliente"].isin(cliente)]

    # Filtro categoría
    if categoria:
        df_filtrado = df_filtrado[df_filtrado["Categoría"].isin(categoria)]

    # Filtro fecha
    inicio= fechas_unicas[rango_fechas[0]]
    fin = fechas_unicas[rango_fechas[1]]
    
    df_filtrado = df_filtrado[
        (df_filtrado["Año-Mes"] >= inicio) &
        (df_filtrado["Año-Mes"] <= fin)
    ]

    # Agrupar
    dfagrupado = df_filtrado.groupby(["Año-Mes", "Categoría"]).agg({
        "OS-Valor Unitario": ["mean", "min", "max"]
    }).reset_index()
    
    # Aplanar las columnas
    dfagrupado.columns = ["Año-Mes", "Categoría", "OS-Valor Unitario_mean", "OS-Valor Unitario_min", "OS-Valor Unitario_max"]

    # Gráfico
    fighistorico = px.line(
        dfagrupado,
        x="Año-Mes",
        y="OS-Valor Unitario_mean",
        color="Categoría",
        markers=True,
        title="Comparativo histórico de costos",
        custom_data=["OS-Valor Unitario_min", "OS-Valor Unitario_max"]
    )
    
    # Actualizar el hovertemplate para mostrar promedio, mínimo y máximo
    fighistorico.update_traces(
        hovertemplate=  
                    "<b>%{fullData.name}</b><br>" +
                    "Año-Mes: %{x}<br>"+
                    "Promedio: %{y:.2f}<br>"+
                    "Mínimo: %{customdata[0]:.2f}<br>"+
                    "Máximo: %{customdata[1]:.2f}"+
                    "<extra></extra>"
    )
    fighistorico.update_layout(
    # 1. Fondo transparente
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    
    # 2. Tipografía Times New Roman
    font=dict(
        family="Times New Roman, Times, serif",
        size=14,
        color="#333333" # Color de letra gris muy oscuro (casi negro)
    ),
    
    # Ajuste opcional de márgenes para que la letra no se corte
    margin=dict(t=80, b=50, l=50, r=50)
    )

    # 3. Líneas de cuadrícula más oscuras
    fighistorico.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1
    )

    fighistorico.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray'
    )
    return fighistorico


# PROMEDIO DE COSTOS POR PROVEEDOR EN CADA CATEGORÍA

# Filtro de categoría
dcc.Dropdown(
    options=[{"label": c, "value": c} 
             for c in df_costos_fechacom["Categoría"].unique()],
    multi=True,
    placeholder="Selecciona categoría",
    id="filtro-categoria-prov"
),

# Filtro de proceso de producción
dcc.Dropdown(
    options=[{"label": p, "value": p} 
             for p in df_costos_fechacom["Proceso Producción"].unique()],
    multi=True,
    placeholder="Selecciona el proceso de produccion",
    id="filtro-servicio"
),

# Filtro de cliente
dcc.Dropdown(
    options=[{"label": c, "value": c} 
             for c in df_costos_fechacom["Cliente"].unique()],
    multi=True,
    placeholder="Selecciona cliente",
    id="filtro-cliente-prov"
),

dcc.DatePickerRange(
    start_date=df_costos_fechacom["Fecha"].min(),
    end_date=df_costos_fechacom["Fecha"].max(),
    display_format="YYYY-MM-DD",
    id="filtro-fecha-prov"
),

dcc.Graph(id="grafico-proveedor-cliente")
@app.callback(
    Output("grafico-proveedor-cliente", "figure"),
    Input("filtro-categoria-prov", "value"),
    Input("filtro-servicio", "value"),
    Input("filtro-cliente-prov", "value"),
    Input("filtro-fecha-prov", "start_date"),
    Input("filtro-fecha-prov", "end_date")
)
def actualizar_prov_cli(categoria, servicio, cliente, start_date, end_date):
    
    if not start_date or not end_date:
        return px.bar(title="Selecciona un rango de fechas")
    
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    df_filtrado1 = df_costos_fechacom.copy()
    # Filtro categoría
    if categoria:
        df_filtrado1 = df_filtrado1[df_filtrado1["Categoría"].isin(categoria)]
    # Filtro proveedor
    if servicio:
        df_filtrado1 = df_filtrado1[df_filtrado1["Proceso Producción"].isin(servicio)]
    # Filtro cliente
    if cliente:
        df_filtrado1 = df_filtrado1[df_filtrado1["Cliente"].isin(cliente)]
        
    if df_filtrado1.empty:
        return px.bar(title="No hay datos con los filtros seleccionados")
    # Filtro fecha
    df_filtrado1 = df_filtrado1[
        (df_filtrado1["Fecha"] >= start_date) &
        (df_filtrado1["Fecha"] <= end_date)
    ]

    df_grouped = df_filtrado1.groupby(["TALLER SERVICIO", "Categoría"]).agg({
        "OS-Valor Unitario": ["mean", "min", "max"],
        'CANTIDAD ENTREGA SATELITE': 'sum'
    }).reset_index()
    
    # Aplanar las columnas
    df_grouped.columns = ["TALLER SERVICIO", "Categoría", "OS-Valor Unitario_mean", "OS-Valor Unitario_min", "OS-Valor Unitario_max", "CANTIDAD ENTREGA SATELITE"]


    figproveedores = px.bar(
        df_grouped,
        x="Categoría",
        y="OS-Valor Unitario_mean",
        color="TALLER SERVICIO",
        barmode="group",
        title="Costo Promedio por Proveedor",
        custom_data=["OS-Valor Unitario_min", "OS-Valor Unitario_max", "CANTIDAD ENTREGA SATELITE"]
    )
    
    # Actualizar el hovertemplate para mostrar promedio, mínimo y máximo
    figproveedores.update_traces(
        hovertemplate=  
                    "<b>%{fullData.name}</b><br>" +
                    "Categoría: %{x}<br>"+
                    "Promedio: %{y:.2f}<br>"+
                    "Mínimo: %{customdata[0]:.2f}<br>"+
                    "Máximo: %{customdata[1]:.2f}"+
                    "Cantidades totales: %{customdata[2]:.2f}"+
                    "<extra></extra>"
    )
  
    
    figproveedores.update_layout(
    # 1. Fondo transparente
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    
    # 2. Tipografía Times New Roman
    font=dict(
        family="Times New Roman, Times, serif",
        size=14,
        color="#333333" # Color de letra gris muy oscuro (casi negro)
    ),
    
    # Ajuste opcional de márgenes para que la letra no se corte
    margin=dict(t=80, b=50, l=50, r=50)
    )

    # 3. Líneas de cuadrícula más oscuras
    figproveedores.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1
    )

    figproveedores.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray'
    )
    return figproveedores


# PARETO DE PROVEEDORES QUE MÁS FACTURAN

dcc.DatePickerRange(
    start_date=df_costos_fechacom["Fecha"].min(),
    end_date=df_costos_fechacom["Fecha"].max(),
    display_format="YYYY-MM-DD",
    id="filtro-fecha-val"
),
dcc.Dropdown(
    options=[{"label": p, "value": p} 
             for p in df_costos_fechacom["Proceso Producción"].unique()],
    multi=True,
    placeholder="Selecciona el proceso de produccion",
    id="filtro-servicio-prov"
),

dcc.Graph(id="grafico-val-prov")
@app.callback(
    Output("grafico-val-prov", "figure"),
    Input("filtro-servicio-prov", "value"),
    Input("filtro-fecha-val", "start_date"),
    Input("filtro-fecha-val", "end_date")
)

def actualizar_val_prov (servicio, start_date, end_date):
    
    if start_date is None or end_date is None:
        raise PreventUpdate
    
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    df_filtrado_prov = df_costos_fechacom.copy()
    
    if servicio:
        df_filtrado_prov = df_filtrado_prov[df_filtrado_prov["Proceso Producción"].isin(servicio)]
    
    if df_filtrado_prov.empty:
        return px.bar(title="No hay datos con los filtros seleccionados")
            
    # Filtro fecha   
    df_filtrado_prov = df_filtrado_prov[
        (df_filtrado_prov["Fecha"] >= start_date) &
        (df_filtrado_prov["Fecha"] <= end_date)
    ]
    
    df_pareto_valorp = df_filtrado_prov.groupby(['OP-D', 'Proceso Producción', 'TALLER SERVICIO', 'Num OS']).agg({
        'CANTIDAD ENTREGA SATELITE': 'mean',
        'Valor total OS': 'mean'
    })
    
    df_pareto_valorpro = df_pareto_valorp.groupby('TALLER SERVICIO').agg({
        'CANTIDAD ENTREGA SATELITE': 'sum',
        'Valor total OS': 'sum'
    }).reset_index()

    # Ordenar por VALOR DE OP 
    df_pareto_valorpro = df_pareto_valorpro.sort_values(by='Valor total OS', ascending=False)

    total_valor_general = df_pareto_valorpro['Valor total OS'].sum()
    df_pareto_valorpro['Porcentaje'] = (df_pareto_valorpro['Valor total OS'] / total_valor_general) * 100
    df_pareto_valorpro['Acumulado'] = df_pareto_valorpro['Porcentaje'].cumsum()
    
    fig_valor_pro = go.Figure()
    # Barras: Valor Total OP por cliente
    fig_valor_pro.add_trace(go.Bar(
        x=df_pareto_valorpro['TALLER SERVICIO'],
        y=df_pareto_valorpro['Valor total OS'],
        name='Valor Total OS ($)',
        marker_color='#632E8B', 
        # Pasamos la columna directamente
        customdata=df_pareto_valorpro['CANTIDAD ENTREGA SATELITE'], 
        hovertemplate=(
            "<b>Proveedor: %{x}</b><br>" +
            "Valor Total OS: %{y:$,.0f}<br>" +
            "Total Prendas: %{customdata:,.0f}<br>" +
            "<extra></extra>"
        )
    ))

    # Línea: % Acumulado
    fig_valor_pro.add_trace(go.Scatter(
        x=df_pareto_valorpro['TALLER SERVICIO'],
        y=df_pareto_valorpro['Acumulado'],
        name='% Acumulado',
        yaxis='y2',
        line=dict(color="#F561F0", width=3),
        hovertemplate="Impacto Acumulado: %{y:.2f}%<extra></extra>"
    ))

    fig_valor_pro.update_layout(
        xaxis=dict(title='Proveedor', tickangle=-45),
        yaxis=dict(title='Valor Total OS ($)'),
        yaxis2=dict(title='Porcentaje Acumulado (%)', overlaying='y', side='right', range=[0, 105]),
        hovermode='x unified',
        template='plotly_white',
        height=700
    )

    # Línea del 80%
    fig_valor_pro.add_shape(type="line", x0=0, x1=1, y0=80, y1=80, yref='y2', xref='paper',
                       line=dict(color="black", width=2, dash="dot"))

    fig_valor_pro.update_layout(
    # 1. Fondo transparente
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    
    # 2. Tipografía Times New Roman
        font=dict(
            family="Times New Roman, Times, serif",
            size=10,
            color="#333333" # Color de letra gris muy oscuro (casi negro)
        ),
    
        # Ajuste opcional de márgenes para que la letra no se corte
        margin=dict(t=80, b=50, l=50, r=50)
        )

        # 3. Líneas de cuadrícula más oscuras
    fig_valor_pro.update_xaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
        linecolor='gray',    # Línea del eje principal en negro
        zeroline=True,        # Mantener la línea del cero...
        zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
        zerolinewidth=1
    )

    fig_valor_pro.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='#bdbdbd', 
        linecolor='gray'
    )
    return fig_valor_pro
    
    
# PARETO DE PROVEEDORES QUE MÁS OS REALIZAN

dcc.DatePickerRange(
    start_date=df_costos_fechacom["Fecha"].min(),
    end_date=df_costos_fechacom["Fecha"].max(),
    display_format="YYYY-MM-DD",
    id="filtro-fecha-vol"
),
dcc.Dropdown(
    options=[{"label": p, "value": p} 
             for p in df_costos_fechacom["Proceso Producción"].unique()],
    multi=True,
    placeholder="Selecciona el proceso de produccion",
    id="filtro-servicio-vol"
),

dcc.Graph(id="grafico-vol-prov")
@app.callback(
    Output("grafico-vol-prov", "figure"),
    Input("filtro-servicio-vol", "value"),
    Input("filtro-fecha-vol", "start_date"),
    Input("filtro-fecha-vol", "end_date")
)

def actualizar_vol_prov (servicio, start_date, end_date):
    
    if start_date is None or end_date is None:
        raise PreventUpdate
    
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    df_filtrado_pro = df_costos_fechacom.copy()
    
    if servicio:
        df_filtrado_pro = df_filtrado_pro[df_filtrado_pro["Proceso Producción"].isin(servicio)]
    
    if df_filtrado_pro.empty:
        return px.bar(title="No hay datos con los filtros seleccionados")
                       
    # Filtro fecha   
    df_filtrado_pro = df_filtrado_pro[
        (df_filtrado_pro["Fecha"] >= start_date) &
        (df_filtrado_pro["Fecha"] <= end_date)
    ]
    
    df_pareto_v = df_filtrado_pro.groupby(['OP-D', 'Proceso Producción', 'TALLER SERVICIO', 'Num OS']).agg({
        'CANTIDAD ENTREGA SATELITE': 'mean',
        'Valor total OS': 'mean'
    })
    
    df_pareto_volu = df_pareto_v.groupby('TALLER SERVICIO').agg({
        'CANTIDAD ENTREGA SATELITE': 'sum',
        'Valor total OS': 'sum'
    }).reset_index()

    # Ordenamos la cantidad de mayor a menor
    df_pareto_volu = df_pareto_volu.sort_values(by='CANTIDAD ENTREGA SATELITE', ascending=False)

    # Cálculo de acumulados sobre el VOLUMEN de producción
    total_prendas = df_pareto_volu['CANTIDAD ENTREGA SATELITE'].sum()
    df_pareto_volu['Porcentaje'] = (df_pareto_volu['CANTIDAD ENTREGA SATELITE'] / total_prendas) * 100
    df_pareto_volu['Acumulado'] = df_pareto_volu['Porcentaje'].cumsum()

    fig_vol = go.Figure()

    # Barras de la cantidad de pedidos por cliente

    fig_vol.add_trace(go.Bar(
        x=df_pareto_volu['TALLER SERVICIO'],
        y=df_pareto_volu['CANTIDAD ENTREGA SATELITE'],
        name='Volumen de Producción (Prendas)',
        marker_color="#632E8B", 
        # Pasamos datos extra al hover/etiqueta
        customdata=df_pareto_volu['Valor total OS'], 
        hovertemplate=( 
        "<b>Proveedor: %{x}</b><br>" +
        "Cantidad de Prendas: %{y:,.0f}<br><br>" +
        "Valor total de OS: %{customdata:,.0f}<br>"
        "<extra></extra>"
        )
    ))

    # Línea del % acumulado
    fig_vol.add_trace(go.Scatter(
        x=df_pareto_volu['TALLER SERVICIO'],
        y=df_pareto_volu['Acumulado'],
        name='% Acumulado Volumen',
        yaxis='y2',
        line=dict(color="#F561F0", width=3),
        hovertemplate="Impacto Acumulado: %{y:.2f}%<extra></extra>"
    ))

    # 6. Layout
    fig_vol.update_layout(
        xaxis=dict(title='Proveedor', tickangle=-45),
        yaxis=dict(title='Cantidad de Prendas Producidas'),
        yaxis2=dict(title='Porcentaje Acumulado (%)', overlaying='y', side='right', range=[0, 105]),
        hovermode='x unified',
        template='plotly_white',
        height=700
    )   

    # Línea del 80% 
    fig_vol.add_shape(type="line", x0=0, x1=1, y0=80, y1=80, yref='y2', xref='paper',
                       line=dict(color="black", width=2, dash="dot"))

    fig_vol.update_layout(
        # 1. Fondo transparente
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    
        # 2. Tipografía Times New Roman
        font=dict(
            family="Times New Roman, Times, serif",
            size=10,
            color="#333333" # Color de letra gris muy oscuro (casi negro)
        ),
    
        # Ajuste opcional de márgenes para que la letra no se corte
        margin=dict(t=80, b=50, l=50, r=50)
    )

    # 3. Líneas de cuadrícula más oscuras
    fig_vol.update_xaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
        linecolor='gray',    # Línea del eje principal en negro
        zeroline=True,        # Mantener la línea del cero...
        zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
        zerolinewidth=1
    )

    fig_vol.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='#bdbdbd', 
        linecolor='gray'
    )
    return fig_vol

# PARETO DE PROVEEDORES A LOS QUE SE LES PAGA SOBREPRECIO

dcc.DatePickerRange(
    start_date=df_costos_fechacom["Fecha"].min(),
    end_date=df_costos_fechacom["Fecha"].max(),
    display_format="YYYY-MM-DD",
    id="filtro-fecha-sobreprecio"
),

dcc.Dropdown(
    options=[{"label": p, "value": p} 
             for p in df_costos_fechacom["Proceso Producción"].unique()],
    multi=True,
    placeholder="Selecciona el proceso de produccion",
    id="filtro-servicio-sobreprecio"
),

dcc.Dropdown(
    options=[{"label": c, "value": c} 
             for c in df_costos_fechacom["Categoría"].unique()],
    multi=True,
    placeholder="Selecciona categoría",
    id="filtro-categoria-sobreprecio"
),

dcc.Graph(id="grafico-sobreprecio-prov")
@app.callback(
    Output("grafico-sobreprecio-prov", "figure"),
    Input("filtro-categoria-sobreprecio", "value"),
    Input("filtro-servicio-sobreprecio", "value"),
    Input("filtro-fecha-sobreprecio", "start_date"),
    Input("filtro-fecha-sobreprecio", "end_date")
)

def actualizar_sob_prov (categoria, servicio, start_date, end_date):
    
    if start_date is None or end_date is None:
        raise PreventUpdate
    
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    df_filtrado_sob = df_costos_fechacom.copy()
    
    if categoria:
        df_filtrado_sob = df_filtrado_sob[df_filtrado_sob["Categoría"].isin(categoria)]
        
    if servicio:
        df_filtrado_sob = df_filtrado_sob[df_filtrado_sob["Proceso Producción"].isin(servicio)]
            
    # Filtro fecha   
    df_filtrado_sob = df_filtrado_sob[
        (df_filtrado_sob["Fecha"] >= start_date) &
        (df_filtrado_sob["Fecha"] <= end_date)
    ]
    
    group_cols = ['Productos', 'Cliente', 'Proceso Producción']

    # Creamos un df agrupando las columnas del paso anterior y el valor de la OS, sacando entre estos datos solo el valor más bajo de la misma agrupacion
    df_minimos = df_filtrado_sob.groupby(group_cols)['OS-Valor Unitario'].transform('min')

    # Del df original (filtrado) creamos una columna de diferencia para ver los valores que son diferentes al minimo que sacamos anteriormente
    df_filtrado_sob['Diferencia_Unitaria'] = df_filtrado_sob['OS-Valor Unitario'] - df_minimos

    # Multiplicamos la columna de diferencia por la cantidad para saber cuánto a nivel general se pagó de más 
    df_filtrado_sob['Ahorro_Potencial_Total'] = df_filtrado_sob['Diferencia_Unitaria'] * df_filtrado_sob['CANTIDAD ENTREGA SATELITE']

    # Agrupación para el gráfico
    df_pareto_ahorro = df_filtrado_sob.groupby('TALLER SERVICIO').agg({
        'Ahorro_Potencial_Total': 'sum',
        'Valor total OS': 'sum',
        'CANTIDAD ENTREGA SATELITE': 'sum',
        'Categoría': lambda x: ', '.join(x.unique())
    }).reset_index()

    df_pareto_ahorro = df_pareto_ahorro.sort_values(by='Ahorro_Potencial_Total', ascending=False)

    # Cálculo de acumulados
    total_ahorro_posible = df_pareto_ahorro['Ahorro_Potencial_Total'].sum()
    df_pareto_ahorro['Porcentaje'] = (df_pareto_ahorro['Ahorro_Potencial_Total'] / total_ahorro_posible) * 100
    df_pareto_ahorro['Acumulado'] = df_pareto_ahorro['Porcentaje'].cumsum()

    fig_ahorro = go.Figure()

    fig_ahorro.add_trace(go.Bar(
        x=df_pareto_ahorro['TALLER SERVICIO'],
        y=df_pareto_ahorro['Ahorro_Potencial_Total'],
        name='Gasto Excedente ($)',
        marker_color="#45007A",
        customdata=df_pareto_ahorro[['Valor total OS', 'Categoría', 'CANTIDAD ENTREGA SATELITE']], 
        hovertemplate=(
            "<b>Proveedor: %{x}</b><br>" +
            "Ahorro potencial total: %{y:$,.0f}<br>" +
            "Valor total de OS: %{customdata[0]:$,.0f}<br>" + 
            "Categorías: %{customdata[1]}<br>" + # <-- QUITAMOS el formato de moneda $:,.0f porque es texto
            "Total Prendas: %{customdata[2]:,.0f}" +
            "<extra></extra>"
        )
    ))

    fig_ahorro.add_trace(go.Scatter(
        x=df_pareto_ahorro['TALLER SERVICIO'],
        y=df_pareto_ahorro['Acumulado'],
        name='% Acumulado',
        yaxis='y2',
        line=dict(color="#F561F0", width=3),
        hovertemplate="Progreso Acumulado: %{y:.2f}%<extra></extra>"
    ))

    # 7. Configuración de Layout
    fig_ahorro.update_layout(
        xaxis=dict(title='Proveedor'),
        yaxis=dict(title='Ahorro Potencial Acumulado ($)'),
        yaxis2=dict(title='Porcentaje (%)', overlaying='y', side='right', range=[0, 105]),
        hovermode='x unified'
    )

    # Línea del 80% (Los proveedores que causan el 80% del sobrecosto)
    fig_ahorro.add_shape(type="line", x0=0, x1=1, y0=80, y1=80, yref='y2', xref='paper',
                     line=dict(color="black", width=2, dash="dot"))

    fig_ahorro.update_layout(
        # 1. Fondo transparente
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    
        # 2. Tipografía Times New Roman
        font=dict(
            family="Times New Roman, Times, serif",
            size=8,
            color="#333333" # Color de letra gris muy oscuro (casi negro)
        ),
    
        # Ajuste opcional de márgenes para que la letra no se corte
        margin=dict(t=80, b=50, l=50, r=50)
    )

    # 3. Líneas de cuadrícula más oscuras
    fig_ahorro.update_xaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
        linecolor='gray',    # Línea del eje principal en negro
        zeroline=True,        # Mantener la línea del cero...
        zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
        zerolinewidth=1
    )

    fig_ahorro.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='#bdbdbd', 
        linecolor='gray'
    )
    return fig_ahorro

# PRENDAS EN LAS QUE SE PUEDE REDUCIR COSTOS

dcc.DatePickerRange(
    start_date=df_costos_fechacom["Fecha"].min(),
    end_date=df_costos_fechacom["Fecha"].max(),
    display_format="YYYY-MM-DD",
    id="filtro-fecha-sobreprecio-prenda"
),

dcc.Graph(id="grafico-sobreprecio-prend")
@app.callback(
    Output("grafico-sobreprecio-prend", "figure"),
    Input("filtro-fecha-sobreprecio-prenda", "start_date"),
    Input("filtro-fecha-sobreprecio-prenda", "end_date")
)
def actualizar_sob_prov (start_date, end_date):
    
    if start_date is None or end_date is None:
        raise PreventUpdate
    
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    df_filtrado_pre = df_costos_fechacom.copy()
            
    # Filtro fecha   
    df_filtrado_pre = df_filtrado_pre[
        (df_filtrado_pre["Fecha"] >= start_date) &
        (df_filtrado_pre["Fecha"] <= end_date)
    ]
    # Utilizamos los mismos cálculos de ahorro que ya habiamos hecho anteriormente (Diferencia_Unitaria y Ahorro_Potencial_Total)

    group_cols = ['Productos', 'Cliente', 'Proceso Producción']
    df_filtrado_pre['min_val'] = df_filtrado_pre.groupby(group_cols)['OS-Valor Unitario'].transform('min')
    df_filtrado_pre['Ahorro_Potencial_Total'] = (df_filtrado_pre['OS-Valor Unitario'] - df_filtrado_pre['min_val']) * df_filtrado_pre['CANTIDAD ENTREGA SATELITE']

    # Agrupamos por categoría, sumamos el ahorro y traemos el conteo de procesos para tener contexto
    df_pareto_pre = df_filtrado_pre.groupby('Categoría').agg({
        'Ahorro_Potencial_Total': 'sum',
        'Valor total OS': 'sum',
        'Proceso Producción': 'nunique' # Cuántos procesos distintos hay en esta categoría
    }).reset_index()

    # 4. Ordenar y Acumulados
    df_pareto_pre = df_pareto_pre.sort_values(by='Ahorro_Potencial_Total', ascending=False)
    total_ahorro_pre = df_pareto_pre['Ahorro_Potencial_Total'].sum()
    df_pareto_pre['Acumulado'] = (df_pareto_pre['Ahorro_Potencial_Total'].cumsum() / total_ahorro_pre) * 100


    fig_cat_ahorro = go.Figure()

    fig_cat_ahorro.add_trace(go.Bar(
        x=df_pareto_pre['Categoría'],
        y=df_pareto_pre['Ahorro_Potencial_Total'],
        name='Oportunidad de Ahorro ($)',
        marker_color='#45007A',
        customdata=df_pareto_pre[['Valor total OS', 'Proceso Producción']],
        hovertemplate=(
            "<b>Categoría: %{x}</b><br>" +
            "Ahorro potencial total: %{y:$,.0f}<br>" +
            "Valor total OS: %{customdata[0]:$,.0f}<br>" +
            "Variedad de Procesos: %{customdata[1]}<extra></extra>"
        )
    ))

    fig_cat_ahorro.add_trace(go.Scatter(
        x=df_pareto_pre['Categoría'],
        y=df_pareto_pre['Acumulado'],
        name='% Acumulado',
        yaxis='y2',
        line=dict(color='#F561F0', width=3),
        hovertemplate="Impacto Acumulado: %{y:.2f}%<extra></extra>"
    ))

    # Layout
    fig_cat_ahorro.update_layout(
        xaxis=dict(title='Categoría'),
        yaxis=dict(title='Ahorro Potencial Total ($)'),
        yaxis2=dict(title='Porcentaje Acumulado (%)', overlaying='y', side='right', range=[0, 105]),
        hovermode='x unified',
        template='plotly_white'
    )

    # Línea del 80%
    fig_cat_ahorro.add_shape(type="line", x0=0, x1=1, y0=80, y1=80, yref='y2', xref='paper',
                  line=dict(color="black", width=2, dash="dot"))

    fig_cat_ahorro.update_layout(
        # 1. Fondo transparente
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    
        # 2. Tipografía Times New Roman
        font=dict(
            family="Times New Roman, Times, serif",
            size=10,
            color="#333333" # Color de letra gris muy oscuro (casi negro)
        ),
    
        # Ajuste opcional de márgenes para que la letra no se corte
        margin=dict(t=80, b=50, l=50, r=50)
    )   

    # 3. Líneas de cuadrícula más oscuras
    fig_cat_ahorro.update_xaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
        linecolor='gray',    # Línea del eje principal en negro
        zeroline=True,        # Mantener la línea del cero...
        zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
        zerolinewidth=1
    )

    fig_cat_ahorro.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='#bdbdbd', 
        linecolor='gray'
    )

    return fig_cat_ahorro

# PARETO TOTAL DE PRENDAS

dcc.DatePickerRange(
    start_date=df_costos_fechacom["Fecha"].min(),
    end_date=df_costos_fechacom["Fecha"].max(),
    display_format="YYYY-MM-DD",
    id="filtro-fecha-categoria"
),

dcc.Graph(id="grafico-categoria")
@app.callback(
    Output("grafico-categoria", "figure"),
    Input("filtro-fecha-categoria", "start_date"),
    Input("filtro-fecha-categoria", "end_date")
)

def actualizar_categoria (start_date, end_date):
    
    if start_date is None or end_date is None:
        raise PreventUpdate
    
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    df_filtrado_cate = df_costos_fechacom.copy()
            
    # Filtro fecha   
    df_filtrado_cate = df_filtrado_cate[
        (df_filtrado_cate["Fecha"] >= start_date) &
        (df_filtrado_cate["Fecha"] <= end_date)
    ]
    
    # Agrupamos por categoria y op detalle para tener las cantidades reales
    df_pareto_voluu = df_filtrado_cate.groupby(['Categoría', 'OP-D']).agg({
        'CANTIDAD ENTREGA SATELITE': 'mean',
        'Valor total OS': 'sum'
    }).reset_index()
      
    df_pareto_vol_cat = df_pareto_voluu.groupby('Categoría').agg({
        'CANTIDAD ENTREGA SATELITE': 'sum',
        'Valor total OS': 'sum'
    }).reset_index()

    # Ordenamos la cantidad de mayor a menor
    df_pareto_vol_cat = df_pareto_vol_cat.sort_values(by='CANTIDAD ENTREGA SATELITE', ascending=False)

    # Cálculo de acumulados sobre el VOLUMEN de producción
    total_prendas = df_pareto_vol_cat['CANTIDAD ENTREGA SATELITE'].sum()
    df_pareto_vol_cat['Porcentaje'] = (df_pareto_vol_cat['CANTIDAD ENTREGA SATELITE'] / total_prendas) * 100
    df_pareto_vol_cat['Acumulado'] = df_pareto_vol_cat['Porcentaje'].cumsum()

    fig_volumenc = go.Figure()

    # Barras de la cantidad de pedidos por cliente

    fig_volumenc.add_trace(go.Bar(
        x=df_pareto_vol_cat['Categoría'],
        y=df_pareto_vol_cat['CANTIDAD ENTREGA SATELITE'],
        name='Volumen de Producción (Prendas)',
        marker_color="#632E8B", 
        # Pasamos datos extra al hover/etiqueta
        customdata=df_pareto_vol_cat[['Valor total OS']], 
        hovertemplate=( 
            "<b>Cliente: %{x}</b><br>" +
            "Cantidad de Prendas: %{y:,.0f}<br><br>" +
            "Valor total de OS: %{customdata[0]:$,.0f}<br>" +
            "<extra></extra>"
        )
    ))

    # Línea del % acumulado
    fig_volumenc.add_trace(go.Scatter(
        x=df_pareto_vol_cat['Categoría'],
        y=df_pareto_vol_cat['Acumulado'],
        name='% Acumulado Volumen',
        yaxis='y2',
        line=dict(color="#F561F0", width=3),
        hovertemplate="Impacto Acumulado: %{y:.2f}%<extra></extra>"
    ))

    # 6. Layout
    fig_volumenc.update_layout(
        xaxis=dict(title='Cat', tickangle=-45),
        yaxis=dict(title='Cantidad de Prendas Producidas'),
        yaxis2=dict(title='Porcentaje Acumulado (%)', overlaying='y', side='right', range=[0, 105]),
        hovermode='x unified',
        template='plotly_white',
        height=700
    )

    # Línea del 80% 
    fig_volumenc.add_shape(type="line", x0=0, x1=1, y0=80, y1=80, yref='y2', xref='paper',
                       line=dict(color="black", width=2, dash="dot"))

    fig_volumenc.update_layout(
        # 1. Fondo transparente
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    
        # 2. Tipografía Times New Roman
        font=dict(
        family="Times New Roman, Times, serif",
        size=10,
        color="#333333" # Color de letra gris muy oscuro (casi negro)
        ),
    
        # Ajuste opcional de márgenes para que la letra no se corte
        margin=dict(t=80, b=50, l=50, r=50)
    )

    # 3. Líneas de cuadrícula más oscuras
    fig_volumenc.update_xaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
        linecolor='gray',    # Línea del eje principal en negro
        zeroline=True,        # Mantener la línea del cero...
        zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
        zerolinewidth=1
    )

    fig_volumenc.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='#bdbdbd', 
        linecolor='gray'
    )
    return fig_volumenc

# PRENDAS CON MAYOR COSTO EN PROCESO DE PRODUCCIÓN

dcc.DatePickerRange(
    start_date=df_costos_fechacom["Fecha"].min(),
    end_date=df_costos_fechacom["Fecha"].max(),
    display_format="YYYY-MM-DD",
    id="filtro-fecha-prod"
),

# Filtro de categoría
dcc.Dropdown(
    options=[{"label": c, "value": c} 
             for c in df_costos_fechacom["Categoría"].unique()],
    multi=True,
    placeholder="Selecciona categoría",
    id="filtro-categoria-prod"
),

dcc.Dropdown(
    options=[{"label": c, "value": c} 
             for c in df_costos_fechacom["Cliente"].unique()],
    multi=True,
    placeholder="Selecciona cliente",
    id="filtro-cliente-prod"
),

dcc.Dropdown(
    options=[{"label": p, "value": p} 
             for p in df_costos_fechacom["Proceso Producción"].unique()],
    multi=True,
    placeholder="Selecciona el proceso de produccion",
    id="filtro-servicio-prod"
),

dcc.Graph(id="grafico-producto")
@app.callback(
    Output("grafico-producto", "figure"),
    Input("filtro-categoria-prod", "value"),
    Input("filtro-cliente-prod", "value"),
    Input("filtro-servicio-prod", "value"),
    Input("filtro-fecha-prod", "start_date"),
    Input("filtro-fecha-prod", "end_date")
)

def actualizarr(categoria, cliente, servicio, start_date, end_date):
    
    if start_date is None or end_date is None:
        raise PreventUpdate
    
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
           
    df_filtrado2 = df_costos_fechacom.copy()
    
    # Filtro categoría
    if categoria:
        df_filtrado2 = df_filtrado2[df_filtrado2["Categoría"].isin(categoria)]
    
    if cliente:
        df_filtrado2 = df_filtrado2[df_filtrado2["Cliente"].isin(cliente)]
        
    if servicio:
        df_filtrado2 = df_filtrado2[df_filtrado2["Proceso Producción"].isin(servicio)]
        
    df_filtrado2 = df_filtrado2[
        (df_filtrado2["Fecha"] >= start_date) &
        (df_filtrado2["Fecha"] <= end_date)
    ]
    
    dfagrup = df_filtrado2.groupby(['Productos', 'TALLER SERVICIO', 'OP-D', 'Proceso Producción', 'Cliente']).agg({
        'Valor total OS': 'mean',
        'CANTIDAD ENTREGA SATELITE':'mean'
    }).reset_index()
          
    top_10_prod = dfagrup.groupby(['Productos', 'OP-D']).agg({
        'Valor total OS': 'sum',
        'CANTIDAD ENTREGA SATELITE': 'sum',
        'Cliente': lambda x: ', '.join(x.unique()),
        'TALLER SERVICIO': lambda x: ', '.join(x.unique())
    }).reset_index()

    filtro = top_10_prod.sort_values(by='Valor total OS', ascending=False)

    filtro['Producto_OP'] = filtro['Productos'] + ' | OP ' + filtro['OP-D'].astype(str)

    figbarrr = px.bar(
        filtro, 
        x='Producto_OP', 
        y='Valor total OS',
        color='Productos',
        category_orders={"Producto_OP": filtro['Producto_OP'].tolist()},
        hover_data={
            'TALLER SERVICIO': True,
            'Cliente': True,
            'OP-D': True,
            'CANTIDAD ENTREGA SATELITE': True,
            'Producto_OP': False,  # para no repetirlo
            'Productos': False      # opcional
        }
    )

    
    figbarrr.update_layout(
        # 1. Fondo transparente
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    
        # 2. Tipografía Times New Roman
        font=dict(
        family="Times New Roman, Times, serif",
        size=10,
        color="#333333" # Color de letra gris muy oscuro (casi negro)
        ),
    
        # Ajuste opcional de márgenes para que la letra no se corte
        margin=dict(t=80, b=50, l=50, r=50)
    )

    # 3. Líneas de cuadrícula más oscuras
    figbarrr.update_xaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
        linecolor='gray',    # Línea del eje principal en negro
        zeroline=True,        # Mantener la línea del cero...
        zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
        zerolinewidth=1
    )

    figbarrr.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='#bdbdbd', 
        linecolor='gray'
    )
    
    return figbarrr

# CLIENTES A LOS QUE MÁS SE LES FABRICA:

dcc.DatePickerRange(
    start_date=df_costos_fechacom["Fecha"].min(),
    end_date=df_costos_fechacom["Fecha"].max(),
    display_format="YYYY-MM-DD",
    id="filtro-fecha-cliente"
),

dcc.Graph(id="grafico-cliente_vol")
@app.callback(
    Output("grafico-cliente_vol", "figure"),
    Input("filtro-fecha-cliente", "start_date"),
    Input("filtro-fecha-cliente", "end_date")
)

def actualizarr(start_date, end_date):
    
    if start_date is None or end_date is None:
        raise PreventUpdate
    
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
           
    df_filtrado_cli = df_costos_fechacom.copy()

    df_ops_unicass = df_filtrado_cli.groupby(['Cliente', 'Num-OP']).agg({
        'Total Precio OP': 'mean', # Sacamos solo el promedio ya que el mismo valor totaal de la op se repite en todas las filas que tienen la misma op
        'OS-Cantidad': 'sum',
        'Valor total OS': 'sum'
    }).reset_index()

    # hacemos la agrupación final para el gráfico
    df_pareto_vol = df_ops_unicass.groupby('Cliente').agg({
        'Total Precio OP': 'sum',
        'OS-Cantidad': 'sum',
        'Valor total OS': 'sum'
    }).reset_index()

    # Ordenamos la cantidad de mayor a menor
    df_pareto_vol = df_pareto_vol.sort_values(by='OS-Cantidad', ascending=False)

    # Cálculo de acumulados sobre el VOLUMEN de producción
    total_prendas = df_pareto_vol['OS-Cantidad'].sum()
    df_pareto_vol['Porcentaje'] = (df_pareto_vol['OS-Cantidad'] / total_prendas) * 100
    df_pareto_vol['Acumulado'] = df_pareto_vol['Porcentaje'].cumsum()

    fig_volumen = go.Figure()

    # Barras de la cantidad de pedidos por cliente

    fig_volumen.add_trace(go.Bar(
        x=df_pareto_vol['Cliente'],
        y=df_pareto_vol['OS-Cantidad'],
        name='Volumen de Producción (Prendas)',
        marker_color="#632E8B", 
        # Pasamos datos extra al hover/etiqueta
        customdata=df_pareto_vol[['Valor total OS','Total Precio OP']], 
        hovertemplate=( 
            "<b>Cliente: %{x}</b><br>" +
            "Cantidad de Prendas: %{y:,.0f}<br><br>" +
            "Valor total de OS: %{customdata[0]:$,.0f}<br>" +
            "Valor total de OP: %{customdata[1]:$,.0f}<br>"
            "<extra></extra>"
        )
    ))

    # Línea del % acumulado
    fig_volumen.add_trace(go.Scatter(
        x=df_pareto_vol['Cliente'],
        y=df_pareto_vol['Acumulado'],
        name='% Acumulado Volumen',
        yaxis='y2',
        line=dict(color="#F561F0", width=3),
        hovertemplate="Impacto Acumulado: %{y:.2f}%<extra></extra>"
    ))

    # 6. Layout
    fig_volumen.update_layout(
        xaxis=dict(title='Cliente', tickangle=-45),
        yaxis=dict(title='Cantidad de Prendas Producidas'),
        yaxis2=dict(title='Porcentaje Acumulado (%)', overlaying='y', side='right', range=[0, 105]),
        hovermode='x unified',
        template='plotly_white',
        height=700
    )

    # Línea del 80% 
    fig_volumen.add_shape(type="line", x0=0, x1=1, y0=80, y1=80, yref='y2', xref='paper',
                       line=dict(color="black", width=2, dash="dot"))

    fig_volumen.update_layout(
        # 1. Fondo transparente
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    
        # 2. Tipografía Times New Roman
        font=dict(
            family="Times New Roman, Times, serif",
            size=10,
            color="#333333" # Color de letra gris muy oscuro (casi negro)
        ),
    
        # Ajuste opcional de márgenes para que la letra no se corte
        margin=dict(t=80, b=50, l=50, r=50)
    )

    # 3. Líneas de cuadrícula más oscuras
    fig_volumen.update_xaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
        linecolor='gray',    # Línea del eje principal en negro
        zeroline=True,        # Mantener la línea del cero...
        zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
        zerolinewidth=1
    )

    fig_volumen.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='#bdbdbd', 
        linecolor='gray'
    )
    return fig_volumen

# CLIENTES CON LOS QUE MÁS SE FACTURA:

dcc.DatePickerRange(
    start_date=df_costos_fechacom["Fecha"].min(),
    end_date=df_costos_fechacom["Fecha"].max(),
    display_format="YYYY-MM-DD",
    id="filtro-fecha-valc"
),

dcc.Graph(id="grafico-cliente_valc")
@app.callback(
    Output("grafico-cliente_valc", "figure"),
    Input("filtro-fecha-valc", "start_date"),
    Input("filtro-fecha-valc", "end_date")
)

def actualizarr(start_date, end_date):
    
    if start_date is None or end_date is None:
        raise PreventUpdate
    
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
           
    df_filtrado_cliente = df_costos_fechacom.copy()
    
    df_ops_unicas = df_filtrado_cliente.groupby(['Cliente', 'Num-OP']).agg({
        'Total Precio OP': 'mean', 
        'OS-Cantidad': 'sum',
        'Valor total OS': 'sum'
    }).reset_index()

    # Agrupar por CLIENTE para el Pareto
    df_pareto_valor = df_ops_unicas.groupby('Cliente').agg({
        'Total Precio OP': 'sum',   # Ahora sí sumamos los valores únicos de sus OPs
        'OS-Cantidad': 'sum',
        'Valor total OS': 'sum'
    }).reset_index()

    # Ordenar por VALOR DE OP 
    df_pareto_valor = df_pareto_valor.sort_values(by='Total Precio OP', ascending=False)


    total_valor_general = df_pareto_valor['Total Precio OP'].sum()
    df_pareto_valor['Porcentaje'] = (df_pareto_valor['Total Precio OP'] / total_valor_general) * 100
    df_pareto_valor['Acumulado'] = df_pareto_valor['Porcentaje'].cumsum()


    fig_valor = go.Figure()

    # Barras: Valor Total OP por cliente
    fig_valor.add_trace(go.Bar(
        x=df_pareto_valor['Cliente'],
        y=df_pareto_valor['Total Precio OP'],
        name='Valor Total OP ($)',
        marker_color='#632E8B', 
        customdata=df_pareto_valor[['Valor total OS', 'OS-Cantidad']], 
        hovertemplate=(
            "<b>Cliente: %{x}</b><br>" +
            "Valor Total OP: %{y:$,.0f}<br>" +
            "Valor Total OS: %{customdata[0]:$,.0f}<br>" +
            "Total Prendas: %{customdata[1]:,.0f}<br>" + # <--- Cambio aquí: :.0f elimina decimales
            "<extra></extra>"
        )
    ))

    # Línea: % Acumulado
    fig_valor.add_trace(go.Scatter(
        x=df_pareto_valor['Cliente'],
        y=df_pareto_valor['Acumulado'],
        name='% Acumulado',
        yaxis='y2',
        line=dict(color="#F561F0", width=3),
        hovertemplate="Impacto Acumulado: %{y:.2f}%<extra></extra>"
    ))

    fig_valor.update_layout(
        xaxis=dict(title='Cliente', tickangle=-45),
        yaxis=dict(title='Valor Total OP ($)'),
        yaxis2=dict(title='Porcentaje Acumulado (%)', overlaying='y', side='right', range=[0, 105]),
        hovermode='x unified',
        template='plotly_white',
        height=700
    )

    # Línea del 80%
    fig_valor.add_shape(type="line", x0=0, x1=1, y0=80, y1=80, yref='y2', xref='paper',
                       line=dict(color="black", width=2, dash="dot"))

    fig_valor.update_layout(
    # 1. Fondo transparente
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    
    # 2. Tipografía Times New Roman
    font=dict(
        family="Times New Roman, Times, serif",
        size=10,
        color="#333333" # Color de letra gris muy oscuro (casi negro)
    ),
    
    # Ajuste opcional de márgenes para que la letra no se corte
    margin=dict(t=80, b=50, l=50, r=50)
    )

    # 3. Líneas de cuadrícula más oscuras
    fig_valor.update_xaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
        linecolor='gray',    # Línea del eje principal en negro
        zeroline=True,        # Mantener la línea del cero...
        zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
        zerolinewidth=1
    )

    fig_valor.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='#bdbdbd', 
        linecolor='gray'
    )
    return fig_valor

# HISTÓRICO DE PAGADO EN SERVICIOS
dcc.Dropdown(
    options=[
        {"label": p, "value":p}
        for p in df_costos_fechacom["Proceso Producción"].unique()],
    multi=True,
    placeholder="Seleccione el servicio",
    id="filtro-servicio-hist"
),

dcc.RangeSlider(
    min=0,
    max=len(fechas_unicas) -1,
    value=[0, len(fechas_unicas) - 1],
    marks=None,
    id="filtro-fecha-hist"
),

dcc.Graph(id="grafico-hist")
@app.callback(
    Output("grafico-hist", "figure"),
    Input("filtro-servicio-hist", "value"),
    Input("filtro-fecha-hist", "value")
)
def actualizar(servicio, rango_fechas):

    df_filtrado_hist = df_costos_fechacom.copy()


    # Filtro fecha
    inicio= fechas_unicas[rango_fechas[0]]
    fin = fechas_unicas[rango_fechas[1]]
    
    df_filtrado_hist = df_filtrado_hist[
        (df_filtrado_hist["Año-Mes"] >= inicio) &
        (df_filtrado_hist["Año-Mes"] <= fin)
    ]
    
    if not servicio:
        # Agrupamos todo en una sola línea llamada "Total General"
        dfagrupadohisto = df_filtrado_hist.groupby(["Año-Mes", "Proceso Producción", "OP-D"]).agg({
            'Valor total OS' : 'mean'
        }).reset_index()
        
        dfagrupadohist = dfagrupadohisto.groupby(["Año-Mes"]).agg({
            'Valor total OS': 'sum'
        }).reset_index()
        
        color_param = None  # No hay distinción de colores por proceso
        dfagrupadohist["Proceso Producción"] = "Total General" # Para que el hover no falle
    
    else:
        # Si hay filtros, aplicamos el filtro de servicio
        df_filtrado_hist = df_filtrado_hist[df_filtrado_hist["Proceso Producción"].isin(servicio)]
        
        # Agrupamos por proceso para ver líneas individuales
        dfagrupadohisto = df_filtrado_hist.groupby(["Año-Mes", "Proceso Producción", "OP-D"]).agg({
            'Valor total OS' : 'mean'
        }).reset_index()
        
        dfagrupadohist = dfagrupadohisto.groupby(["Año-Mes", "Proceso Producción"]).agg({
            'Valor total OS' : 'sum'
        }).reset_index()
        
        color_param = "Proceso Producción"

    # 3. Gráfico
    fighist = px.line(
        dfagrupadohist,
        x="Año-Mes",
        y="Valor total OS",
        color=color_param, # Será None si no hay filtro, o "Proceso..." si lo hay
        markers=True,
        title="Comparativo histórico de costos en servicios",
        # Usamos Libre Franklin como hablamos antes
        template="plotly_white" 
    )
    
    
    fighist.update_layout(
        # 1. Fondo transparente
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    
        font=dict(
            family="Libre Franklin, sans-serif", # <--- Cambia esto
            size=11,                             # Ajusta el tamaño si es necesario
            color="#482b63" 
        ),
        # Ajuste opcional de márgenes para que la letra no se corte
        margin=dict(t=80, b=50, l=50, r=50)
    )

    # 3. Líneas de cuadrícula más oscuras
    fighist.update_xaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
        linecolor='gray',    # Línea del eje principal en negro
        zeroline=True,        # Mantener la línea del cero...
        zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
        zerolinewidth=1
    )

    fighist.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='#bdbdbd', 
        linecolor='gray'
    )
    return fighist

#HISTÓRICO DE FACTURADO EN TOTAL

dcc.RangeSlider(
    min=0,
    max=len(fechas_unicas) -1,
    value=[0, len(fechas_unicas) - 1],
    marks=None,
    id="filtro-fecha-histo"
),

dcc.Graph(id="grafico-histo")
@app.callback(
    Output("grafico-histo", "figure"),
    Input("filtro-fecha-histo", "value")
)

def actualizar( rango_fechas):

    df_filtrado_histo = df_costos_fechacom.copy()

    # Filtro fecha
    inicio= fechas_unicas[rango_fechas[0]]
    fin = fechas_unicas[rango_fechas[1]]
    
    df_filtrado_histo = df_filtrado_histo[
        (df_filtrado_histo["Año-Mes"] >= inicio) &
        (df_filtrado_histo["Año-Mes"] <= fin)
    ]
    
    dfagrupadohisto = df_filtrado_histo.groupby(["Año-Mes",'Num-OP']).agg({
            'Total Precio OP' : 'mean'
    }).reset_index()
        
    dfagrupadohist = dfagrupadohisto.groupby(["Año-Mes"]).agg({
            'Total Precio OP': 'sum'
    }).reset_index()

    # 3. Gráfico
    fighisto = px.line(
        dfagrupadohist,
        x="Año-Mes",
        y="Total Precio OP",
        markers=True,
        title="Comparativo histórico de facturado",
        template="plotly_white" 
    )
    
    
    fighisto.update_layout(
        # 1. Fondo transparente
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    
        font=dict(
            family="Libre Franklin, sans-serif", # <--- Cambia esto
            size=11,                             # Ajusta el tamaño si es necesario
            color="#482b63" 
        ),
        # Ajuste opcional de márgenes para que la letra no se corte
        margin=dict(t=80, b=50, l=50, r=50)
    )

    # 3. Líneas de cuadrícula más oscuras
    fighisto.update_xaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
        linecolor='gray',    # Línea del eje principal en negro
        zeroline=True,        # Mantener la línea del cero...
        zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
        zerolinewidth=1
    )

    fighisto.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='#bdbdbd', 
        linecolor='gray'
    )
    return fighisto

app.layout = html.Div([
    # páginas
    dcc.Tabs([
        # PÁGINA 1    
        dcc.Tab(label="📊 INFORME DE COSTOS", 
                className="custom-tab",
                selected_className="custom-tab--selected",
                children=[
            
        html.Div([

        html.Img(src="/assets/logo.png", className="logo left"),
        html.Div("INFORME DE COSTOS MOLT", className="title"),
        html.Img(src="/assets/logo.png", className="logo right"),
        
        ], className="header"),
        
        # INTRODUCCIÓN
        html.Div([
            html.H3("📌 CONTEXTO DEL ANÁLISIS"),

            html.P([
                "En el presente informe encontrará dos secciones principales. En la primera, denominada ",
                html.B("Procesos de producción"),
                ", se recopilan los datos de los últimos 6 meses relacionados con los costos de los servicios (valores antes de IVA), ",
                "incluyendo tanto el valor costeado por el área comercial como el valor realmente pagado en la OS. ",
                "Aquí encontrará gráficos diseñados para facilitar el análisis y apoyar la toma de decisiones."
            ]),

            html.P([
                "En la segunda sección, ",
                html.B("Informe de costos"),
                ", se presentan los graficos correspondientes a los proveedores que más producen y a los que más se les paga y el análisis desglozado de estos datos, así mismo,",
                "encontramos los datos por clientes que mas facturan para la compañía y que más esfuerzo llevan a nivel producción, todos los datos relacionados los podra filtrar por fecha,",
                "y demás variables con el fin de facilitar el análisis en diferentes periodos de tiempo y comparaciones."
            ]),

            html.P([
                "Adicionalmente, se incluyen visualizaciones del comportamiento histórico de variables clave, permitiendo entender su evolución a lo largo del tiempo."
            ]),

            html.P(["Para una mejor lectura del informe, se recomienda tener en cuenta los siguientes conceptos:"]),

            html.Ul([

            html.Li([
                html.B("Cuando hablamos de Diferencia de valor unitario = "),
                "Valor Unitario OS - Valor Unitario Costeado"
            ]),

            html.Li([

                html.B("Diferencia de valor total = "),
                "Valor Total OS - Valor Total Costeado"
            ]),

            html.Li([
                "Si el valor de la Orden de Satélite es mayor al costeado → ",
                html.B("subcosteo"),
                " para la compañía, significa un sobrecosto total"
            ]),
            
            html.Li([
                "Si el valor costeado por el comercial es mayor al valor de la orden de satélite → ",
                html.B("sobrecosteo"),
                " para la compañía, significa un 'ahorro' total"
            ])
        ])
        ],className="info-box")
        ]),

        # PÁGINA 2      
        dcc.Tab(label="PROCESOS DE PRODUCCIÓN", 
                className="custom-tab",
                selected_className="custom-tab--selected",
                children=[
            
        # KPI'S
        html.Div([
            html.Div("INFORME DE COSTOS DE SERVICIOS", className="title")
        ], className="header"),
        
        html.Div([
            html.Div([
                html.H2("SOBRECOSTEO TOTAL", style={"color": "#2E7D32"}),
                html.Div(ahorro_total_fmt, className="kpi-value", style={"color": "#4CAF50"}),
                html.P("Tomamos la diferencia de valor total y sumamos solo los valores negativos, así obtenemos el total general de sobrecosteo")
            ], className="card kpi"),

            html.Div([
                html.H2("BALANCE NETO"),
                html.Div(balance_total_fmt, className="kpi-value"),
                html.P("Finalmente la suma de todos los valores tanto positivos como negativos nos da este valor correspondiente a un sobrecosteo, es decir, un ahorro para la compañía")
            ], className="card kpi"),

            html.Div([
                html.H2("SUBCOSTEO TOTAL", style={"color": "#C62828"}),
                html.Div(perdida_total_fmt, className="kpi-value", style={"color": "#E53935"}),
                html.P("Tomamos la diferencia de valor total y sumamos solo los valores positivos, así obtenemos el total general de subcosteo")
            ], className="card kpi"),

        ], className="row"),

        # Gráfico 1 impacto económico en cada proceso de producción
        html.Div([
            html.Div([
                html.H3("IMPACTO ECONÓMICO TOTAL DE CADA PROCESO DE PRODUCCIÓN"),
                dcc.Graph(figure=figimpactoservicio),
                html.P(["Para este gráfico tomamos la diferencia de valor total,",
                        "realizamos los cálculos correspondientes para obtener el valor total del impacto económico tanto sobrecosteado",
                        "como subcosteado en cada proceso de producción, así mismo, tenemos el balance,",
                        "si este se encuentra sobre 0 implica un Subcosteo y si se encuentra debajo de 0 un sobrecosteo"])
            ], className="card")
        ], className="row"),

        # Gráfico 2 cajas y bigotes de la diferencia de costo unitario en cada proceso de producción
        html.Div([
            html.Div([
                html.H3("DIFERENCIA DE COSTO UNITARIO"),
                dcc.Graph(figure=figboxplot),
                html.P("En este gráfico tomamos la diferencia de costo unitario para visualizar cómo varía esta diferencia en cada uno de los procesos de producción, los puntos por encima de 0 representan un subcosteo y los que están por debajo un sobrecosteo.")
            ], className="card")
        ], className="row"),

        # Gráfico 3 cajas y bigotes de la diferencia de costo total en cada proceso de producción
        html.Div([
            html.Div([
                html.H3("DIFERENCIA DE COSTO TOTAL"),
                dcc.Graph(figure=figboxtotal),
                html.P("En este gráfico tomamos la diferencia de costo total para visualizar cómo varía esta diferencia en cada uno de los procesos de producción, los puntos por encima de 0 representan un subcosteo y los que están por debajo un sobrecosteo.")        
            ], className="card")
        ], className="row"),
        
        # Gráfico 4 cajas y bigotes de la diferencia de costo total en cada proceso de producción
        html.Div([
            html.Div([
                html.H3("TOP 5 CATEGORÍAS CON MAYOR IMPACTO ECONÓMICO CON RESPECTO A LA DIFERENCIA DE VALOR UNITARIO"),
                dcc.Graph(figure=fig_dif),
                html.P("Este gráfico muestra la variación del costo unitario frente al promedio en cada categoría y proceso de producción. Nos permite visualizar las 5 categorías un una mayor variación en la diferencia de costo unitario")        
            ], className="card")
        ], className="row"),
        
        html.Div([
            html.Div([
                html.H3("TOP CATEGORÍAS CON PROCESO DE PRODUCCIÓN DE MÁS IMPACTO ECONÓMICO PARA LA COMPAÑÍA"),
                dcc.Graph(figure=fig_total),
                html.P("Tomamos un top 10 de las categorías que más impacto económico han tenido en los últimos 6 meses en la compañía y en qué proceso de producción se presentó este impacto")        
            ], className="card")
        ], className="row"),
        
        html.Div([
            html.Div([
                html.H3("MAPA DE CALOR PROMEDIO DE COSTEO POR CATEGORIA DE CADA COMERCIAL"),
                dcc.Graph(figure=figcomercial),
                html.P("Sacamos el promedio de la diferencia de costo unitario por comercial, así sabemos en qué procesos de producción suelen sobrecostear o subcostear normalmente")        
            ], className="card")
        ], className="row"),
        
        # Botones por proceso de producción dentro de la pagina 2
        dcc.Tabs(
        className="sub-tabs",
        children=[ 
            dcc.Tab(
            label="SELECCIONAR 👉",
            className="sub-tab",
            selected_className="sub-tab--selected",
            children=[
                html.Div([
                    html.H2("MOLT", style={"opacity": "0.5", "color":"#7166B0"}),
                    html.P("Selecciona un proceso arriba para ver los detalles.")
                ], style={"textAlign": "center", "padding": "50px", "color":"#7166B0"})
            ]),
            
            # CONFECCIÓN
            
            dcc.Tab(
            label="CONFECCIÓN",
            className="sub-tab",
            selected_className="sub-tab--selected",
            children=[
                html.Div([
                    html.Div([
                        html.H3("IMPACTO DE LA DIFERENCIA DE COSTO UNITARIO EN EL PROCESO DE CONFECCIÓN"),
                            dcc.Graph(figure=fig_confe),
                        html.P("En esta gráfica encontramos la visual de los ahorros y sobrecostos que tiene la diferencia de valores en el proceso de confección, los puntos por encima de la diagonal representan un sobrecosto y los que se encuentran por debajo un subcosteo")        
                    ], className="card")
                ], className="row"),
                
                html.Div([
                    html.Div([
                        html.H3("IMPACTO ECONÓMICO DEL PROCESO DE CONFECCIÓN EN LA COMPAÑÍA"),
                            dcc.Graph(figure=fig),
                        html.P("En esta gráfica vemos el top 10 de las OP con mayor impacto económico para la compañía teniendo en cuenta la diferencia total entre el valor costeado y pagado")        
                    ], className="card")
                ], className="row")    
            ]),

            # SUBLIMACIÓN
            
            dcc.Tab(
            label="SUBLIMACIÓN",
            className="sub-tab",
            selected_className="sub-tab--selected",
            children=[
                html.Div([
                    html.Div([
                        html.H3("IMPACTO DE LA DIFERENCIA DE COSTO UNITARIO EN EL PROCESO DE SUBLIMACIÓN"),
                            dcc.Graph(figure=fig_subl),
                        html.P("En esta gráfica encontramos la visual de los ahorros y sobrecostos que tiene la diferencia de valores en el proceso de sublimación, los puntos por encima de la diagonal representan un sobrecosto y los que se encuentran por debajo un subcosteo")        
                    ], className="card")
                ], className="row"),
                
                html.Div([
                    html.Div([
                        html.H3("IMPACTO ECONÓMICO DE LAS DIFERENCIAS DE COSTOS DEL PROCESO DE SUBLIMACIÓN EN LA COMPAÑÍA"),
                            dcc.Graph(figure=fig_sub),
                        html.P("En esta gráfica vemos las OP con mayor impacto económico para la compañía teniendo en cuenta la diferencia total entre el valor costeado y pagado")        
                    ], className="card")
                ], className="row")
            ]),
            
            #BORDADO

            dcc.Tab(
            label="BORDADO",
            className="sub-tab",
            selected_className="sub-tab--selected",
            children=[
                html.Div([
                    html.Div([
                        html.H3("IMPACTO DE LA DIFERENCIA DE COSTO UNITARIO EN EL PROCESO DE BORDADO"),
                            dcc.Graph(figure=fig_bordado),
                        html.P("En esta gráfica encontramos la visual de los ahorros y sobrecostos que tiene la diferencia de valores en el proceso de bordado, los puntos por encima de la diagonal representan un sobrecosto y los que se encuentran por debajo un subcosteo")        
                    ], className="card")
                ], className="row"),
                
                html.Div([
                    html.Div([
                        html.H3("IMPACTO ECONÓMICO DE LAS DIFERENCIAS DE COSTOS DEL PROCESO DE BORDADO EN LA COMPAÑÍA"),
                            dcc.Graph(figure=fig_bord),
                        html.P("En esta gráfica vemos las OP con mayor impacto económico para la compañía teniendo en cuenta la diferencia total entre el valor costeado y pagado")        
                    ], className="card")
                ], className="row")                
            ]),
            
            #ESTAMPADO

            dcc.Tab(
            label="ESTAMPADO",
            className="sub-tab",
            selected_className="sub-tab--selected",
            children=[
                html.Div([
                    html.Div([
                        html.H3("IMPACTO DE LA DIFERENCIA DE COSTO UNITARIO EN EL PROCESO DE ESTAMPADO"),
                            dcc.Graph(figure=fig_estampado),
                        html.P("En esta gráfica encontramos la visual de los ahorros y sobrecostos que tiene la diferencia de valores en el proceso de estampado, los puntos por encima de la diagonal representan un sobrecosto y los que se encuentran por debajo un subcosteo")        
                    ], className="card")
                ], className="row"),
                
                html.Div([
                    html.Div([
                        html.H3("IMPACTO ECONÓMICO DE LAS DIFERENCIAS DE COSTOS DEL PROCESO DE ESTAMPADO EN LA COMPAÑÍA"),
                            dcc.Graph(figure=fig_est),
                        html.P("En esta gráfica vemos las OP con mayor impacto económico para la compañía teniendo en cuenta la diferencia total entre el valor costeado y pagado")        
                    ], className="card")
                ], className="row")
            ]),
            
            # PAQUETE SIN MARCA

            dcc.Tab(
            label="PQT SIN MARCA",
            className="sub-tab",
            selected_className="sub-tab--selected",
            children=[
                html.Div([
                    html.Div([
                        html.H3("IMPACTO DE LA DIFERENCIA DE COSTO UNITARIO EN EL SERVICIO DE PAQUETE COMPLETO SIN MARCA"),
                            dcc.Graph(figure=fig_pqt_sin),
                        html.P("En esta gráfica encontramos la visual de los ahorros y sobrecostos que tiene la diferencia de valores en el servicio de paquete completo sin marca, los puntos por encima de la diagonal representan un sobrecosto y los que se encuentran por debajo un subcosteo")        
                    ], className="card")
                ], className="row"),
                
                html.Div([
                    html.Div([
                        html.H3("IMPACTO ECONÓMICO DE LAS DIFERENCIAS DE COSTOS DEL SERVICIO DE PAQUETE COMPLETO SIN MARCA EN LA COMPAÑÍA"),
                            dcc.Graph(figure=fig_pqt_sinM),
                        html.P("En esta gráfica vemos las OP con mayor impacto económico para la compañía teniendo en cuenta la diferencia total entre el valor costeado y pagado")        
                    ], className="card")
                ], className="row")
            ]),
            
            # PRELAVADO

            dcc.Tab(
            label="PRELAVADO",
            className="sub-tab",
            selected_className="sub-tab--selected",
            children=[
                html.Div([
                    html.Div([
                        html.H3("IMPACTO DE LA DIFERENCIA DE COSTO UNITARIO EN EL PROCESO DE PRELAVADO"),
                            dcc.Graph(figure=fig_pre),
                        html.P("En esta gráfica encontramos la visual de los ahorros y sobrecostos que tiene la diferencia de valores en el proceso de prelavao, los puntos por encima de la diagonal representan un sobrecosto y los que se encuentran por debajo un subcosteo")        
                    ], className="card")
                ], className="row"),
                
                html.Div([
                    html.Div([
                        html.H3("IMPACTO ECONÓMICO DE LAS DIFERENCIAS DE COSTOS DEL PROCESO DE PRELAVADO  EN LA COMPAÑÍA"),
                            dcc.Graph(figure=fig_prelavado),
                        html.P("En esta gráfica vemos las OP con mayor impacto económico para la compañía teniendo en cuenta la diferencia total entre el valor costeado y pagado.")        
                    ], className="card")
                ], className="row")               
            ]),
            
            # CORTE Y CONFECCIÓN

            dcc.Tab(
            label="CORTE Y CONFECCION",
            className="sub-tab",
            selected_className="sub-tab--selected",
            children=[
                html.Div([
                    html.Div([
                        html.H3("IMPACTO DE LA DIFERENCIA DE COSTO UNITARIO EN EL PROCESO DE CORTE Y CONFECCIÓN"),
                            dcc.Graph(figure=fig_cyc),
                        html.P("En esta gráfica encontramos la visual de los ahorros y sobrecostos que tiene la diferencia de valores en el proceso de corte y confección, los puntos por encima de la diagonal representan un sobrecosto y los que se encuentran por debajo un subcosteo")        
                    ], className="card"),
                ], className="row"),
                
                html.Div([
                    html.Div([
                        html.H3("IMPACTO ECONÓMICO DE LAS DIFERENCIAS DE COSTOS DEL PROCESO DE CORTE Y CONFECCIÓN EN LA COMPAÑÍA"),
                            dcc.Graph(figure=fig_cycc),
                        html.P("En esta gráfica vemos las OP con mayor impacto económico para la compañía teniendo en cuenta la diferencia total entre el valor costeado y pagado")        
                    ], className="card"),
                ], className="row")
            ]),
            
            # PAQUETE COMPLETO

            dcc.Tab(
            label="PAQUETE COMPLETO",
            className="sub-tab",
            selected_className="sub-tab--selected",
            children=[
                html.Div([
                    html.Div([
                        html.H3("IMPACTO DE LA DIFERENCIA DE COSTO UNITARIO EN EL SERVICIO DE PAQUETE COMPLETO"),
                            dcc.Graph(figure=fig_pqt_com),
                        html.P("En esta gráfica encontramos la visual de los ahorros y sobrecostos que tiene la diferencia de valores en el servicio de paquete completo, los puntos por encima de la diagonal representan un sobrecosto y los que se encuentran por debajo un subcosteo")        
                    ], className="card"),
                ], className="row"),
                
                html.Div([
                    html.Div([
                        html.H3("IMPACTO ECONÓMICO DE LAS DIFERENCIAS DE COSTOS DEL SERVICIO DE PAQUETE COMPLETO EN LA COMPAÑÍA"),
                            dcc.Graph(figure=fig_pqtcom),
                        html.P("En esta gráfica vemos las OP con mayor impacto económico para la compañía teniendo en cuenta la diferencia total entre el valor costeado y pagado")        
                    ], className="card"),
                ], className="row")
            ]),
        ])
        ]),
        
        # PÁGINA 3      
        dcc.Tab(label="ANÁLISIS DE COSTOS", 
                className="custom-tab",
                selected_className="custom-tab--selected",
                children=[
            
        html.Div([
            html.Div("ANÁLISIS ESTRATÉGICO COSTOS", className="title")
        ], className="header"),
        
        html.Div([
            html.Div([
                html.H3("¿A QUÉ PROVEEDORES SE LES PAGA MÁS EN TOTAL?"),                
                html.Div([
                dcc.DatePickerRange(
                    start_date=df_costos_fechacom["Fecha"].min(),
                    end_date=df_costos_fechacom["Fecha"].max(),
                    display_format="YYYY-MM-DD",
                    id="filtro-fecha-val"
                ),
                dcc.Dropdown(
                    options=[{"label": p, "value": p} 
                        for p in df_costos_fechacom["Proceso Producción"].unique()],
                    multi=True,
                    placeholder="Selecciona el servicio",
                    id="filtro-servicio-prov"
                )], style={"margin-bottom": "20px"}),

                dcc.Graph(id="grafico-val-prov"),

                html.P("Para este gráfico comparamos a los proveedores en los que más se invierte dinero en las OS, agregamos el filtro de fecha y servicio con el fin de comparar entre los mismos valores")
            ], className="card")
        ], className="row"),  
        
        html.Div([
            html.Div([
                html.H3("¿QUÉ PROVEEDORES REALIZAN LA MAYOR CANTIDAD DE OS?"),                
                html.Div([
                dcc.DatePickerRange(
                    start_date=df_costos_fechacom["Fecha"].min(),
                    end_date=df_costos_fechacom["Fecha"].max(),
                    display_format="YYYY-MM-DD",
                    id="filtro-fecha-vol"
                ),
                dcc.Dropdown(
                    options=[{"label": p, "value": p} 
                        for p in df_costos_fechacom["Proceso Producción"].unique()],
                    multi=True,
                    placeholder="Selecciona el proceso de produccion",
                    id="filtro-servicio-vol"
                )], style={"margin-bottom": "20px"}),

                dcc.Graph(id="grafico-vol-prov"),

                html.P("En este gráfico recolectamos los datos de los proveedores que más servicios producen y cuántos proucen en determinados rangos de fecha")
            ], className="card")
        ], className="row"),  
        
        html.Div([
            html.Div([
                html.H3("¿A QUÉ PROVEEDORES LES ESTAMOS PAGANDO SOBREPRECIO?"),                
                html.Div([
                dcc.DatePickerRange(
                    start_date=df_costos_fechacom["Fecha"].min(),
                    end_date=df_costos_fechacom["Fecha"].max(),
                    display_format="YYYY-MM-DD",
                    id="filtro-fecha-sobreprecio"
                ), 
                dcc.Dropdown(
                    options=[{"label": p, "value": p} 
                        for p in df_costos_fechacom["Proceso Producción"].unique()],
                    multi=True,
                    placeholder="Selecciona el proceso de produccion",
                    id="filtro-servicio-sobreprecio"
                ),

                dcc.Dropdown(
                options=[{"label": c, "value": c} 
                    for c in df_costos_fechacom["Categoría"].unique()],
                multi=True,
                placeholder="Selecciona categoría",
                id="filtro-categoria-sobreprecio"
                )], style={"margin-bottom": "20px"}),

                dcc.Graph(id="grafico-sobreprecio-prov"),

                html.P("En este gráfico utilizamos el mismo grupo de datos (Servicio, Cliente y producto). Dentro de cada grupo, comparamos el valor de las órdenes de satélite entre proveedores, tomando como referencia a los que tienen el menor costo. A partir de esto, calculamos la diferencia de precio frente a los demás proveedores, con el fin de identificar a cuáles les estamos pagando más de lo que podríamos pagar con opciones más económicas.")
            ], className="card")
        ], className="row"),
        
        html.Div([
            html.Div([
                html.H3("¿CUÁLES SON LAS PRENDAS QUE MÁS SE FABRICAN?"),                
                html.Div([
                dcc.DatePickerRange(
                    start_date=df_costos_fechacom["Fecha"].min(),
                    end_date=df_costos_fechacom["Fecha"].max(),
                    display_format="YYYY-MM-DD",
                    id="filtro-fecha-categoria"
                )], style={"margin-bottom": "20px"}),

                dcc.Graph(id="grafico-categoria"),
                html.P("Podemos visualizar las prendas que más se fabrican en volumen")
            ], className="card")
        ], className="row"),
        
        html.Div([
            html.Div([
                html.H3("PRENDAS CON MAYOR COSTO EN LOS PROCESOS DE PRODUCCIÓN"),                
                html.Div([
                dcc.Dropdown(
                    options=[{"label": c, "value": c} 
                        for c in df_costos_fechacom["Categoría"].unique()],
                    multi=True,
                    placeholder="Selecciona categoría",
                    id="filtro-categoria-prod"
                ),
                
                dcc.Dropdown(
                    options=[{"label": c, "value": c} 
                        for c in df_costos_fechacom["Cliente"].unique()],
                    multi=True,
                    placeholder="Selecciona cliente",
                    id="filtro-cliente-prod"
                ),
                
                dcc.Dropdown(
                    options=[{"label": p, "value": p} 
                        for p in df_costos_fechacom["Proceso Producción"].unique()],
                    multi=True,
                    placeholder="Selecciona el proceso de produccion",
                    id="filtro-servicio-prod"
                ),
                
                dcc.DatePickerRange(
                    start_date=df_costos_fechacom["Fecha"].min(),
                    end_date=df_costos_fechacom["Fecha"].max(),
                    display_format="YYYY-MM-DD",
                    id="filtro-fecha-prod"
                )], style={"margin-bottom": "20px"}),

                dcc.Graph(id="grafico-producto"),
                
                html.P("...")
            ], className="card")
        ], className="row"),
        
        html.Div([
            html.Div([
                html.H3("EVOLUCIÓN HISTÓRICA DE COSTOS"),
                
                html.Div([
                dcc.Dropdown(
                options=[{"label": c, "value": c} 
                     for c in df_costos_fechacom["Cliente"].unique()],
                multi=True,
                placeholder="Selecciona el cliente",
                id="filtro-cliente"
                ),

                dcc.Dropdown(
                options=[{"label": c, "value": c} 
                     for c in df_costos_fechacom["Categoría"].unique()],
                multi=True,
                placeholder="Selecciona la categoría",
                id="filtro-categoria"
                )], style={"margin-bottom": "20px"}),

                dcc.Graph(id="grafico-historico"),
                
                html.Div([
                dcc.RangeSlider(
                min=0,
                max=len(fechas_unicas) -1,
                value=[0, len(fechas_unicas) - 1],
                marks=None,
                id="filtro-fecha"
                )], style={"margin-bottom": "20px"}),

                html.P("En este gráfico encontramos la evolución a través del tiempo de los costos de cada categoría utilizada por cada cliente")
            ], className="card")
        ], className="row"),
        
        html.Div([
            html.Div([
                html.H3("¿EN QUÉ PRENDAS ESPECÍFICAS PODEMOS REDUCIR COSTOS?"),                
                html.Div([
                dcc.DatePickerRange(
                    start_date=df_costos_fechacom["Fecha"].min(),
                    end_date=df_costos_fechacom["Fecha"].max(),
                    display_format="YYYY-MM-DD",
                    id="filtro-fecha-sobreprecio-prenda"
                )], style={"margin-bottom": "20px"}),
                
                dcc.Graph(id="grafico-sobreprecio-prend"),
                html.P("...")
            ], className="card")
        ], className="row"),
        
        html.Div([
            html.Div([
                html.H3("PROMEDIO DE COSTOS POR PROVEEDOR EN CADA CATEGORÍA"),
                
                html.Div([
                dcc.Dropdown(
                options=[{"label": c, "value": c} 
                    for c in df_costos_fechacom["Categoría"].unique()],
                    multi=True,
                    placeholder="Selecciona categoría",
                id="filtro-categoria-prov"
                ),

                # Filtro de proveedor
                dcc.Dropdown(
                options=[{"label": p, "value": p} 
                    for p in df_costos_fechacom["Proceso Producción"].unique()],
                    multi=True,
                    placeholder="Selecciona el proceso de produccion",
                    id="filtro-servicio"
                ),

                # Filtro de cliente
                dcc.Dropdown(
                options=[{"label": c, "value": c} 
                    for c in df_costos_fechacom["Cliente"].unique()],
                    multi=True,
                    placeholder="Selecciona cliente",
                id="filtro-cliente-prov"
                ),

                # Slider de fecha
                dcc.DatePickerRange(
                start_date=df_costos_fechacom["Fecha"].min(),
                end_date=df_costos_fechacom["Fecha"].max(),
                display_format="YYYY-MM-DD",
                id="filtro-fecha-prov"
                )], style={"margin-bottom": "20px"}),
                
                dcc.Graph(id="grafico-proveedor-cliente"),
                
                html.P("Para este gráfico tenemos el promedio del costo pagado a cada proveedor en las diferentes categorías, filtramos por cliente ya que los precios pueden variar entre clientes")
            ], className="card")
        ], className="row"),
                
        html.Div([
            html.Div([
                html.H3("¿EN QUÉ CLIENTES SE CONCENTRA LA MAYOR CARGA OPERATIVA?"),                
                html.Div([
                dcc.DatePickerRange(
                    start_date=df_costos_fechacom["Fecha"].min(),
                    end_date=df_costos_fechacom["Fecha"].max(),
                    display_format="YYYY-MM-DD",
                    id="filtro-fecha-cliente"
                )], style={"margin-bottom": "20px"}),
                
                dcc.Graph(id="grafico-cliente_vol"),
                html.P("...")
            ], className="card")
        ], className="row"),
        
        html.Div([
            html.Div([
                html.H3("¿QUÉ CLIENTES REPRESENTAN EL MAYOR INGRESO PRESUPUESTADO A LA COMPAÑÍA?"),                
                html.Div([
                dcc.DatePickerRange(
                    start_date=df_costos_fechacom["Fecha"].min(),
                    end_date=df_costos_fechacom["Fecha"].max(),
                    display_format="YYYY-MM-DD",
                    id="filtro-fecha-valc"
                )], style={"margin-bottom": "20px"}),
                
                dcc.Graph(id="grafico-cliente_valc"),
                html.P("...")
            ], className="card")
        ], className="row"),
        
        html.Div([
            html.Div([
                html.H3("HISTÓRICO DE TOTAL PAGADO EN OS"),                
                html.Div([
                dcc.Dropdown(
                    options=[
                        {"label": p, "value":p}
                        for p in df_costos_fechacom["Proceso Producción"].unique()],
                    multi=True,
                    placeholder="Seleccione el servicio",
                    id="filtro-servicio-hist"
                ),

                dcc.RangeSlider(
                    min=0,
                    max=len(fechas_unicas) -1,
                    value=[0, len(fechas_unicas) - 1],
                    marks=None,
                    id="filtro-fecha-hist"
                )], style={"margin-bottom": "20px"}),

                dcc.Graph(id="grafico-hist"),
                
                html.P("...")
            ], className="card")
        ], className="row"),
        
        html.Div([
            html.Div([
                html.H3("HISTÓRICO DE TOTAL FACTURADO EN OP's"),                
                html.Div([
                dcc.RangeSlider(
                    min=0,
                    max=len(fechas_unicas) -1,
                    value=[0, len(fechas_unicas) - 1],
                    marks=None,
                    id="filtro-fecha-histo"
                )], style={"margin-bottom": "20px"}),

                dcc.Graph(id="grafico-histo"),
                
                html.P("...")
            ], className="card")
        ], className="row"),
        
        ]),
        
        # PAGINA 4
        dcc.Tab(label="ANÁLISIS DE INSUMOS Y MP", 
                className="custom-tab",
                selected_className="custom-tab--selected",
                children=[
                    
        html.Div([
            html.Div("ANÁLISIS DE MATERIAS PRIMAS E INSUMOS", className="title")
        ], className="header"),            
                    
        ])
    ]),
])

if __name__ == "__main__":
    app.run(debug=True)