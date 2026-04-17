# %% [markdown]
# # ANÁLISIS DE LOS COSTOS DE PROCESO DE PRODUCCIÓN

# %% [markdown]
# ## Extracción y limpieza de los datos

# %%
# Importamos las librerías necesarias para el desarrollo del código
import pandas as pd
import plotly.express as px
import re
import unicodedata
import plotly.graph_objects as go

# Primer Excel utilizado para todo el análisis inicial
df_costos = pd.read_excel('df_finall.xlsx')

# Segundo excel con categorías organizadas y fechas desde 2023
df_costos_fechacom = pd.read_excel('dffinn.xlsx')

# Tercer excel con fechas desde 2023 y valor completo de la op pero sin categorías
df_costos_valorop = pd.read_excel('dffinn.xlsx')


# %%
# Definimos la lista de categorías oficiales para la clasificación de productos
categorias_oficiales = [
    'Accesorios', 'Bata', 'Bermuda', 'Blusa', 'Bolígrafo', 'Botas', 'Botella', 'Botón', 'Broche', 'Buzo', 'Camibuzo', 
    'Camiseta', 'Camisa', 'Cachuchera', 'Casco', 'Chaleco', 'Chaqueta', 'Cinta', 'Cofia', 'Conjunto', 'Cordón', 
    'Cremallera', 'Cuello', 'Delantal', 'Diseño', 'Embone', 'Falda', 'Gafas seguridad', 'Gorra', 'Gorro', 'Guantes', 
    'Guata', 'Hilo', 'Hoodie', 'Impermeable', 'Jean', 'Libreta', 'Lonchera', 'Mangas', 'Marquilla', 'Máscara', 'Medias', 
    'Morral', 'Ojalete', 'Overol', 'Pantalón', 'Pantaloneta', 'Pañoleta', 'Paraguas', 'Pavas', 'Polainas', 'Resorte', 
    'Ropa interior', 'Saco', 'Sastre', 'Servicios', 'Sesgo', 'Sudadera', 'Suéter', 'Tankas', 'Tapabocas', 
    'Tapaoídos', 'Tecnología', 'Termo', 'Uniformes', 'Velcro', 'Zapatos', 'Escafandra'
]

# Creamos una función para normalizar el texto, eliminando acentos y convirtiendo a minúsculas
def normalizar(texto):
    texto = str(texto).lower()
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
    return texto

# Creamos una función que clasifique los productos en las categorías oficiales.
def clasificar(Producto):
    producto_norm = normalizar(Producto)
    # Recorremos cada categoría oficial y verificamos si alguna de las palabras está presente en el nombre del producto
    for cat in categorias_oficiales:
        cat_norm = normalizar(cat)
        pattern = r'\b' + re.escape(cat_norm) + r'\b'
        # asignamos la categoría correspondiente si encontramos una coincidencia
        if re.search(pattern, producto_norm):
            return cat
    # Si no encontramos coincidencia, asignamos 'Otros'
    return 'Otros'

#df_costos['Categoría'] = df_costos['Producto'].apply(clasificar)   
#print(df_costos['Categoría'].value_counts())
#df_costos['Proceso Producción'].unique()

paleta_molt_oscura = ["#29104A", "#4A1B8C", "#0F0530", "#3C1053", "#5C2B92"]
paleta_contraste_oscuro = ["#3C1053", "#003F5C", "#005F4B", "#6B2D3A", "#2F4F4F"]
paleta_textil = ["#5B46DF", "#4E6E58", "#A0522D", "#607B8B", "#8B4513"]

# %% [markdown]
# ## KPI
# %%
ahorro_total = abs(df_costos.loc[df_costos['Diferencia'] < 0, 'Diferencia'].sum())
perdida_total = df_costos.loc[df_costos['Diferencia'] > 0, 'Diferencia'].sum()
balance_total = df_costos['Diferencia'].sum()

ahorro_total_fmt = f"{ahorro_total:,.0f}"
perdida_total_fmt = f"{perdida_total:,.0f}"
balance_total_fmt = f"{balance_total:,.0f}"

# %% [markdown]
# ## Pareto
# %% [markdown]
# ### Pareto de proveedor

# %%
df_costos_fechacom['Fecha'] = pd.to_datetime(df_costos_fechacom['Fecha'])

# Filtro de los últimos 6 meses
df_filtrado = df_costos_fechacom[df_costos_fechacom['Fecha'] >= '2025-03-17'].copy()

# Creamos una variable para agrupar las tres columnas y poder comparar sobre los mismos datos
group_cols = ['Categoría', 'Cliente', 'Proceso Producción']

# Creamos un df agrupando las columnas del paso anterior y el valor de la OS, sacando entre estos datos solo el valor más bajo de la misma agrupacion
df_minimos = df_filtrado.groupby(group_cols)['OS-Valor Unitario'].transform('min')

# Del df original (filtrado) creamos una columna de diferencia para ver los valores que son diferentes al minimo que sacamos anteriormente
df_filtrado['Diferencia_Unitaria'] = df_filtrado['OS-Valor Unitario'] - df_minimos

# Multiplicamos la columna de diferencia por la cantidad para saber cuánto a nivel general se pagó de más 
df_filtrado['Ahorro_Potencial_Total'] = df_filtrado['Diferencia_Unitaria'] * df_filtrado['OS-Cantidad']

# Agrupación para el gráfico
df_pareto_ahorro = df_filtrado.groupby('OS-Proveedor').agg({
    'Ahorro_Potencial_Total': 'sum',
    'Valor total OS': 'sum',
    'OS-Cantidad': 'sum'
}).reset_index()


df_pareto_ahorro = df_pareto_ahorro.sort_values(by='Ahorro_Potencial_Total', ascending=False)

# Cálculo de acumulados
total_ahorro_posible = df_pareto_ahorro['Ahorro_Potencial_Total'].sum()
df_pareto_ahorro['Porcentaje'] = (df_pareto_ahorro['Ahorro_Potencial_Total'] / total_ahorro_posible) * 100
df_pareto_ahorro['Acumulado'] = df_pareto_ahorro['Porcentaje'].cumsum()


fig_ahorro = go.Figure()

fig_ahorro.add_trace(go.Bar(
    x=df_pareto_ahorro['OS-Proveedor'],
    y=df_pareto_ahorro['Ahorro_Potencial_Total'],
    name='Gasto Excedente ($)',
    marker_color='#EF553B',
    customdata=df_pareto_ahorro[['Valor total OS', 'OS-Cantidad']], 
    hovertemplate=(
        "<b>Proveedor: %{x}</b><br>" +
        "Ahorro potencial total: %{y:$,.0f}<br>" +
        "Valor total de OS: %{customdata[0]:$,.0f}<br>" + 
        "Total Prendas: %{customdata[1]:,.0f}" +
        "<extra></extra>"
    )
))


fig_ahorro.add_trace(go.Scatter(
    x=df_pareto_ahorro['OS-Proveedor'],
    y=df_pareto_ahorro['Acumulado'],
    name='% Acumulado',
    yaxis='y2',
    line=dict(color='#636EFA', width=3),
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
        size=10,
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


# %% [markdown]
# ### Pareto de Cliente
# %%
# Filtro de fecha para tomar exactamente un año 
df_filtrado_cli = df_costos_valorop[df_costos_valorop['Fecha'] >= '2025-03-17'].copy()

# Agrupamos por el cliente y el número de la OP para sacar el valor exacto de la OP
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

# %%
df_filtrado_cliente = df_costos_valorop[df_costos_valorop['Fecha'] >= '2025-03-17'].copy()

# Agrupar por OP para no duplicar el 'Total Precio OP'
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



# %% [markdown]
# ### Pareto categorías

# %%
df_filtrado_cat = df_costos_fechacom[df_costos_fechacom['Fecha'] >= '2025-03-17'].copy()

# Utilizamos los mismos cálculos de ahorro que ya habiamos hecho anteriormente (Diferencia_Unitaria y Ahorro_Potencial_Total)

group_cols = ['Categoría', 'Cliente', 'Proceso Producción']
df_filtrado_cat['min_val'] = df_filtrado_cat.groupby(group_cols)['OS-Valor Unitario'].transform('min')
df_filtrado_cat['Ahorro_Potencial_Total'] = (df_filtrado_cat['OS-Valor Unitario'] - df_filtrado_cat['min_val']) * df_filtrado_cat['OS-Cantidad']

# Agrupamos por categoría, sumamos el ahorro y traemos el conteo de procesos para tener contexto
df_pareto_cat = df_filtrado_cat.groupby('Categoría').agg({
    'Ahorro_Potencial_Total': 'sum',
    'Valor total OS': 'sum',
    'Proceso Producción': 'nunique' # Cuántos procesos distintos hay en esta categoría
}).reset_index()

# 4. Ordenar y Acumulados
df_pareto_cat = df_pareto_cat.sort_values(by='Ahorro_Potencial_Total', ascending=False)
total_ahorro_cat = df_pareto_cat['Ahorro_Potencial_Total'].sum()
df_pareto_cat['Acumulado'] = (df_pareto_cat['Ahorro_Potencial_Total'].cumsum() / total_ahorro_cat) * 100


fig_cat_ahorro = go.Figure()

fig_cat_ahorro.add_trace(go.Bar(
    x=df_pareto_cat['Categoría'],
    y=df_pareto_cat['Ahorro_Potencial_Total'],
    name='Oportunidad de Ahorro ($)',
    marker_color='#632E8B',
    customdata=df_pareto_cat[['Valor total OS', 'Proceso Producción']],
    hovertemplate=(
        "<b>Categoría: %{x}</b><br>" +
        "Ahorro potencial total: %{y:$,.0f}<br>" +
        "Valor total OS: %{customdata[0]:$,.0f}<br>" +
        "Variedad de Procesos: %{customdata[1]}<extra></extra>"
    )
))

fig_cat_ahorro.add_trace(go.Scatter(
    x=df_pareto_cat['Categoría'],
    y=df_pareto_cat['Acumulado'],
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

# %% [markdown]
# ## Gráfico impacto total por servicio

# %%
df_impacto = df_costos.copy()

df_impacto['Sobrecosteo'] = df_impacto['Diferencia'].apply(lambda x: abs(x) if x < 0 else 0)
df_impacto['Subcosteo'] = df_impacto['Diferencia'].apply(lambda x: x if x > 0 else 0)

df_resumen = df_impacto.groupby('Proceso Producción').agg({
    'Sobrecosteo': 'sum',
    'Subcosteo': 'sum',
    'Diferencia': 'sum'
}).reset_index()

df_resumen = df_resumen.rename(columns={'Diferencia': 'Balance'})

df_melt = df_resumen.melt(
    id_vars='Proceso Producción',
    value_vars=['Sobrecosteo', 'Subcosteo', 'Balance'],
    var_name='tipo',
    value_name='valor'
)

figimpactoservicio = px.bar(
    df_melt,
    x='Proceso Producción',
    y='valor',
    color='tipo',
    barmode='group',
    color_discrete_map={
        'Sobrecosteo': '#2E7D32',      # verde elegante
        'Subcosteo': '#C62828',  # rojo fuerte
        'Balance': '#424242'      # gris neutro
    }
)

df_balance = df_melt[df_melt['tipo'] == 'Balance'].copy()
procesos_orden = df_melt['Proceso Producción'].unique()
df_balance = df_balance.set_index('Proceso Producción').reindex(procesos_orden).reset_index()
df_balance['cumsum'] = df_balance['valor'].cumsum()

# Calcular porcentajes
total_balance = df_balance['cumsum'].iloc[-1]
df_balance['porcentaje'] = (df_balance['cumsum'] / total_balance * 100).round(1)

figimpactoservicio.add_trace(go.Scatter(
    x=df_balance['Proceso Producción'],
    y=df_balance['cumsum'],
    mode='lines+markers+text',
    name='Curva Acumulativa Balance',
    line=dict(color='#424242', width=2),
    text=df_balance['porcentaje'].astype(str) + '%',
    textposition='top left',
    textfont=dict(color='#424242', size=10)
))

df_ahorro = df_melt[df_melt['tipo'] == 'Sobrecosteo'].copy()
procesos_orden_ahorro = df_melt['Proceso Producción'].unique()
df_ahorro = df_ahorro.set_index('Proceso Producción').reindex(procesos_orden_ahorro).reset_index()
df_ahorro['cumsum'] = df_ahorro['valor'].cumsum()

# Calcular porcentajes para Sobrecosteo
total_ahorro = df_ahorro['cumsum'].iloc[-1]
df_ahorro['porcentaje'] = (df_ahorro['cumsum'] / total_ahorro * 100).round(1)

figimpactoservicio.add_trace(go.Scatter(
    x=df_ahorro['Proceso Producción'],
    y=df_ahorro['cumsum'],
    mode='lines+markers+text',
    name='Curva Acumulativa Sobrecosteo',
    line=dict(color='#2E7D32', width=2),
    text=df_ahorro['porcentaje'].astype(str) + '%',
    textposition='bottom right',
    textfont=dict(color='#2E7D32', size=10)
))

df_sobrecosto = df_melt[df_melt['tipo'] == 'Subcosteo'].copy()
procesos_orden_sobrecosto = df_melt['Proceso Producción'].unique()
df_sobrecosto = df_sobrecosto.set_index('Proceso Producción').reindex(procesos_orden_sobrecosto).reset_index()
df_sobrecosto['cumsum'] = df_sobrecosto['valor'].cumsum()

# Calcular porcentajes para Subcosteo
total_sobrecosto = df_sobrecosto['cumsum'].iloc[-1]
df_sobrecosto['porcentaje'] = (df_sobrecosto['cumsum'] / total_sobrecosto * 100).round(1)

figimpactoservicio.add_trace(go.Scatter(
    x=df_sobrecosto['Proceso Producción'],
    y=df_sobrecosto['cumsum'],
    mode='lines+markers+text',
    name='Curva Acumulativa Subcosteo',
    line=dict(color='#C62828', width=2),
    text=df_sobrecosto['porcentaje'].astype(str) + '%',
    textposition='bottom left',
    textfont=dict(color='#C62828', size=10)
))

figimpactoservicio.update_layout(
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
figimpactoservicio.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1
)

figimpactoservicio.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray'
)


# %% [markdown]
# ## BOXPLOT de la diferencia de costos en cada proceso de producción

# %%
# Creamos un gráfico de caja para visualizar la distribución de la diferencia del valor unitario por proceso de producción
df_costos.columns = df_costos.columns.str.strip()

df_costos['Proceso Producción'] = pd.Categorical(
    df_costos['Proceso Producción'],
    categories=sorted(df_costos['Proceso Producción'].astype(str).unique()),
    ordered=True
)

figboxplot = px.box(df_costos, 
             x='Proceso Producción', 
             y='Diferencia valor unitario', 
             points='outliers',
             notched=True,
             color='Proceso Producción',
             hover_data = ['OP Det', 'Nombre del Comercial', 'OS-Cantidad', 'OS-Valor Unitario', 'costo_antes_iva'],
             color_discrete_sequence=paleta_textil,
             category_orders={'Proceso Producción': sorted(df_costos['Proceso Producción'].astype(str).unique())})

figboxplot.update_layout(
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
figboxplot.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1
)

figboxplot.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray'
)


# %% [markdown]
# ## BOXPLOT Diferencia de valor total

# %%
df_costos.columns = df_costos.columns.str.strip()
figboxtotal = px.box(df_costos, 
             x='Proceso Producción', 
             y='Diferencia', 
             points='outliers',
             notched=True,
             color='Proceso Producción',
             hover_data = ['OP Det', 'Nombre del Comercial', 'OS-Cantidad', 'OS-Valor Unitario', 'costo_antes_iva' ],
             color_discrete_sequence=paleta_textil,
             category_orders={'Proceso Producción': sorted(df_costos['Proceso Producción'].astype(str).unique())})

figboxtotal.update_layout(
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
figboxtotal.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1
)

figboxtotal.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray'
)


# %% [markdown]
# ## BOXPLOT coeficiente de variación en categorías por diferencia de valor unitario

# %%
# Utilizamos el promedio de la diferencia para identificar las 5 categorías con mayor impacto económico.
# --- PASO A: Seleccionar los 5 que más dinero mueven (Impacto Real) ---

# --- PASO 1: Top 5 basado en el impacto absoluto total ---
top5_categorias = (
    df_costos.groupby('Categoría')['Diferencia']
    .apply(lambda x: x.abs().sum()) 
    .sort_values(ascending=False)
    .head(5)
    .index.tolist()
)

df_filtrado = df_costos[df_costos['Categoría'].isin(top5_categorias)].copy()

# --- PASO 2: Gráfica con VALORES REALES ---
fig_dif = px.box(
    df_filtrado, 
    x='Categoría', 
    y='Diferencia',
    color='Proceso Producción',
    points='outliers',
    hover_data=['OP Det', 'Nombre del Comercial', 'OS-Cantidad', 'Valor total OS', 'valor total op'],
    labels={
        "Nombre del Comercial": "Comercial",
        "Valor total OS": "Valor total pagado (OS)",
        "valor total op": "Valor total costeado",
        "OS-Cantidad": "Cantidad OS",
        "Diferencia": "Diferencia ($)"
    },
    color_discrete_sequence=paleta_textil
)


# La línea en cero ahora sí significa "Costo Exacto según Presupuesto"
fig_dif.add_hline(y=0, line_dash="dash", line_color="blue")

fig_dif.update_layout(
    boxmode='group',
    yaxis_title="Diferencia de Costo Real ($)",
    xaxis_title="Top 5 Categorías con Mayor Impacto Económico"
)


fig_dif.update_layout(
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
fig_dif.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1
)

fig_dif.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray'
)

# %% [markdown]
# ## Impacto económico general

# %%
# Sumamos la diferencia por OP para que solo exista una barra por etiqueta
df_consolidado_total = df_costos.groupby(['Categoría', 'Proceso Producción']).agg({
    'Diferencia': 'sum'
}).reset_index()

# Ahora sí calculamos el impacto absoluto sobre el total de la OP
df_consolidado_total['abs_impacto'] = df_consolidado_total['Diferencia'].abs()

top_impacto_total = df_consolidado_total.sort_values(by='abs_impacto', ascending=False).head(20)

top_impacto_total = top_impacto_total.sort_values(by='Diferencia', ascending=False)

top_impacto_total['Etiqueta'] = top_impacto_total['Categoría'] + " (" + top_impacto_total['Proceso Producción'].astype(str) + ")"

# Agregar la columna estado basada en Diferencia
top_impacto_total['estado'] = top_impacto_total['Diferencia'].apply(
    lambda x: 'Ahorro' if x < 0 else 'Sobrecosto'
)

fig_total = px.bar(
    top_impacto_total,
    x='Diferencia',
    y='Etiqueta',
    orientation='h',
    color='estado',
    color_discrete_map={'Ahorro': 'green', 'Sobrecosto': 'red'},
)

# Esto elimina las líneas negras que dividen los segmentos dentro de la barra
fig_total.update_traces(marker_line_width=0) 
fig_total.update_layout(
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
fig_total.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1
)

fig_total.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray'
)

# %% [markdown]
# ## Impacto económico por comercial

# %%
import numpy as np

df_heatmap = df_costos.pivot_table(
    index='Nombre del Comercial',
    columns='Proceso Producción',
    values='Diferencia',
    aggfunc='sum'  # puedes cambiar a sum si quieres impacto total
)
df_mediana = df_costos.pivot_table(
    index='Nombre del Comercial',
    columns='Proceso Producción',
    values='Diferencia valor unitario',
    aggfunc='median'
)

df_media = df_costos.pivot_table(
    index='Nombre del Comercial',
    columns='Proceso Producción',
    values='Diferencia valor unitario',
    aggfunc='mean'
)
df_media = df_media.reindex_like(df_heatmap).fillna(0)
df_mediana = df_mediana.reindex_like(df_heatmap).fillna(0)

customdata = np.dstack((
    df_media.values,
    df_mediana.values
))

figcomercial = px.imshow(
    df_heatmap,
    text_auto=True,
    color_continuous_scale='RdYlGn_r',  
    aspect='auto'
)

figcomercial.update_traces(
    customdata=customdata,
    hovertemplate=
        "Comercial: %{y}<br>" +
        "Proceso: %{x}<br><br>" +
        "Diferencia: %{z:,.0f}<br>" +
        "Media: %{customdata[0]:,.0f}<br>" +
        "Mediana: %{customdata[1]:,.0f}<br>" +
        "<extra></extra>"
)

# Limitar escala a percentil 95 para mejor visualización de diferencias
percentil = np.percentile(np.abs(df_heatmap.values), 95)

figcomercial.update_layout(
    # Centrar escala de color en 0 (usando percentil para evitar valores extremos)
    coloraxis=dict(
        cmin=-1000000,
        cmax=1000000,
        cmid=0
    ),
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
figcomercial.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1
)

figcomercial.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray'
)

# %%

# %% [markdown]
# ## Valor costeado vs pagado en margen de ahorro o sobrecosto

# %% [markdown]
# ### Confección

# %%
df_confeccion = df_costos[df_costos['Proceso Producción'] == 'Confección'].copy()

# 1. Agregamos las columnas necesarias en el groupby
# Usamos 'first' para comercial porque siempre es el mismo para una misma OP
df_consolidado = df_confeccion.groupby(['Categoría', 'OP Det']).agg({
    'Diferencia': 'sum',
    'Nombre del Comercial': 'first', 
    'Valor total OS': 'sum',
    'valor total op': 'sum'
}).reset_index()

df_consolidado['abs_impacto'] = df_consolidado['Diferencia'].abs()

# ... (tus pasos de top_sobrecosto, top_ahorro y concat se mantienen igual) ...
top_sobrecosto = df_consolidado.nlargest(10, 'Diferencia')
top_ahorro = df_consolidado.nsmallest(10, 'Diferencia')
top_impacto = pd.concat([top_sobrecosto, top_ahorro], ignore_index=True)
top_impacto = top_impacto.sort_values(by='Diferencia', ascending=False)

top_impacto['Etiqueta'] = top_impacto['Categoría'] + " (OP: " + top_impacto['OP Det'].astype(str) + ")"
top_impacto['estado'] = top_impacto['Diferencia'].apply(lambda x: 'Ahorro' if x < 0 else 'Sobrecosto')

# 2. Configuramos el gráfico con hover_data y labels
# 1. Asegúrate de que el hover_data tenga las 3 columnas en este orden exacto
fig = px.bar(
    top_impacto,
    x='Diferencia',
    y='Etiqueta',
    orientation='h',
    color='estado',
    color_discrete_map={'Ahorro': 'green', 'Sobrecosto': 'red'},
    hover_data=['Nombre del Comercial', 'Valor total OS', 'valor total op'], # [0], [1], [2]
    labels={
        "Nombre del Comercial": "Comercial",
        "Valor total OS": "Valor total pagado",
        "valor total op": "Valor total presupuestado",
        "Diferencia": "Desviación ($)"
    }
)

# 2. Ajustamos el template para que llame a cada dato por su posición
fig.update_traces(
    marker_line_width=0,
    hovertemplate=(
        "<b>%{y}</b><br>" +
        "Diferencia: %{x:$,.0f}<br>" +
        "Comercial: %{customdata[0]}<br>" +
        "Pagado: %{customdata[1]:$,.0f}<br>" +
        "Costeado: %{customdata[2]:$,.0f}" + # <-- Agregamos el índice [2]
        "<extra></extra>"
    )
)
# Esto elimina las líneas negras que dividen los segmentos dentro de la barra
fig.update_traces(marker_line_width=0) 
fig.update_layout(
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
fig.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1
)

fig.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray'
)


# %%
# Filtramos el DF para obtener solo los datos de confección.
df_conf = df_costos[df_costos['Proceso Producción'] == 'Confección'].copy()

# Definimos una columna de estado para tener el contexto de qué significa cada punto en la gráfica.
df_conf['estado'] = df_conf.apply(
    lambda 
    x: 'Ahorro' 
    if x['OS-Valor Unitario'] < x['costo_antes_iva'] 
    else 'Sobrecosto',
    axis=1
)

# Creamos la gráfica de confección, lo que esta encima de la línea diagonal es ahorro y lo que esta debajo es sobrecosto
# El tamaño de cada punto representa el impacto económico

fig_confe = px.scatter(
    df_conf,
    x='OS-Valor Unitario',
    y='costo_antes_iva',
    color='Categoría',
    color_discrete_sequence=paleta_textil,
    hover_data=['OP Det', 'Nombre del Comercial', 'Costeo_Producto', 'OS-Valor Unitario', 'costo_antes_iva'],
    title='Confección'
)

min_val = min(df_conf['costo_antes_iva'].min(), df_conf['OS-Valor Unitario'].min())
max_val = max(df_conf['costo_antes_iva'].max(), df_conf['OS-Valor Unitario'].max())

fig_confe.add_shape(
    type="line",
    x0=min_val, y0=min_val,
    x1=max_val, y1=max_val,
    line=dict(color="pink", dash="dash")
)
fig_confe.update_traces(marker=dict(size=5)) 

fig_confe.update_layout(
    # 1. Fondo transparente
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    
    # 2. Tipografía Times New Roman
    font=dict(
        family="Times New Roman, Times, serif",
        size=12,
        color="#333333" # Color de letra gris muy oscuro (casi negro)
    ),
    
    # Ajuste opcional de márgenes para que la letra no se corte
    margin=dict(t=80, b=50, l=50, r=50)
)

# 3. Líneas de cuadrícula más oscuras
fig_confe.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1,
    title='Costo OS antes IVA'
)

fig_confe.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray',
    title='Costo antes IVA (costeado)'
)


# %% [markdown]
# ### Sublimación

# %%
# Filtramos el DF para obtener solo los datos de sublimación.
df_subl = df_costos[df_costos['Proceso Producción'] == 'Sublimación'].copy()

# Definimos una columna de estado para tener el contexto de qué significa cada punto en la gráfica.
df_subl['estado'] = df_subl.apply(
    lambda 
    x: 'Ahorro' 
    if x['OS-Valor Unitario'] < x['costo_antes_iva'] 
    else 'Sobrecosto',
    axis=1
)


fig_subl= px.scatter(
    df_subl,
    x='OS-Valor Unitario',
    y='costo_antes_iva',
    color='OP Det',
    color_discrete_sequence=paleta_textil,
    hover_data=['OP Det', 'Nombre del Comercial', 'OS-Valor Unitario', 'costo_antes_iva'],
    title='Sublimación'
)

min_val = min(df_subl['costo_antes_iva'].min(), df_subl['OS-Valor Unitario'].min())
max_val = max(df_subl['costo_antes_iva'].max(), df_subl['OS-Valor Unitario'].max())

fig_subl.add_shape(
    type="line",
    x0=min_val, y0=min_val,
    x1=max_val, y1=max_val,
    line=dict(color="pink", dash="dash")
)
fig_subl.update_traces(marker=dict(size=15)) 



fig_subl.update_layout(
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
fig_subl.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1,
    title='Costo OS antes IVA'
)

fig_subl.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray',
    title='Costo antes IVA (costeado)'
)


# %%
df_subli = df_costos[df_costos['Proceso Producción'] == 'Sublimación']

df_consolidado_subl = df_subli.groupby(['Categoría', 'OP Det']).agg({
    'Diferencia': 'sum',
    'Nombre del Comercial': 'first', 
    'Valor total OS': 'sum',
    'valor total op': 'sum'
}).reset_index()

df_consolidado_subl['abs_impacto'] = df_consolidado_subl['Diferencia'].abs()

# ... (tus pasos de top_sobrecosto, top_ahorro y concat se mantienen igual) ...
top_sobrecosto_sub = df_consolidado_subl.nlargest(10, 'Diferencia')
top_ahorro_sub = df_consolidado_subl.nsmallest(10, 'Diferencia')
top_impacto_sub = pd.concat([top_sobrecosto_sub, top_ahorro_sub], ignore_index=True)
top_impacto_sub = top_impacto_sub.sort_values(by='Diferencia', ascending=False)

top_impacto_sub['Etiqueta'] = top_impacto_sub['Categoría'] + " (OP: " + top_impacto_sub['OP Det'].astype(str) + ")"
top_impacto_sub['estado'] = top_impacto_sub['Diferencia'].apply(lambda x: 'Ahorro' if x < 0 else 'Sobrecosto')

# 2. Configuramos el gráfico con hover_data y labels
# 1. Asegúrate de que el hover_data tenga las 3 columnas en este orden exacto
fig_sub = px.bar(
    top_impacto_sub,
    x='Diferencia',
    y='Etiqueta',
    orientation='h',
    color='estado',
    color_discrete_map={'Ahorro': 'green', 'Sobrecosto': 'red'},
    hover_data=['Nombre del Comercial', 'Valor total OS', 'valor total op'], # [0], [1], [2]
    labels={
        "Nombre del Comercial": "Comercial",
        "Valor total OS": "Valor total pagado",
        "valor total op": "Valor total presupuestado",
        "Diferencia": "Desviación ($)"
    }
)

# 2. Ajustamos el template para que llame a cada dato por su posición
fig_sub.update_traces(
    marker_line_width=0,
    hovertemplate=(
        "<b>%{y}</b><br>" +
        "Diferencia: %{x:$,.0f}<br>" +
        "Comercial: %{customdata[0]}<br>" +
        "Pagado: %{customdata[1]:$,.0f}<br>" +
        "Costeado: %{customdata[2]:$,.0f}" + # <-- Agregamos el índice [2]
        "<extra></extra>"
    )
)

# Esto elimina las líneas negras que dividen los segmentos dentro de la barra
fig_sub.update_traces(marker_line_width=0) 
fig_sub.update_layout(
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
fig_sub.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1
)

fig_sub.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray'
)

# %% [markdown]
# ### Bordado

# %%
# Filtramos el DF para obtener solo los datos de Bordado.
df_bord = df_costos[df_costos['Proceso Producción'] == 'Bordado'].copy()

# Definimos una columna de estado para tener el contexto de qué significa cada punto en la gráfica.
df_bord['estado'] = df_bord.apply(
    lambda 
    x: 'Ahorro' 
    if x['OS-Valor Unitario'] < x['costo_antes_iva'] 
    else 'Sobrecosto',
    axis=1
)

# Creamos la gráfica de bordado, lo que esta encima de la línea diagonal es ahorro y lo que esta debajo es sobrecosto
# El tamaño de cada punto representa el impacto económico

fig_bordado= px.scatter(
    df_bord,
    x='OS-Valor Unitario',
    y='costo_antes_iva',
    color='Categoría',
    color_discrete_sequence=paleta_textil,
    hover_data=['OP Det', 'Nombre del Comercial', 'Costeo_Producto', 'OS-Valor Unitario', 'costo_antes_iva'],
    title='Bordado',
)

min_val = min(df_bord['costo_antes_iva'].min(), df_bord['OS-Valor Unitario'].min())
max_val = max(df_bord['costo_antes_iva'].max(), df_bord['OS-Valor Unitario'].max())

fig_bordado.add_shape(
    type="line",
    x0=min_val, y0=min_val,
    x1=max_val, y1=max_val,
    line=dict(color="pink", dash="dash")
)

fig_bordado.update_traces(marker=dict(size=5)) 

fig_bordado.update_layout(
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
fig_bordado.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1,
    title='Costo OS antes IVA'
)

fig_bordado.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray',
    title='Costo antes IVA (costeado)'
)


# %%
df_bord = df_costos[df_costos['Proceso Producción'] == 'Bordado']

# Sumamos la diferencia por OP para que solo exista una barra por etiqueta
df_consolidado_bord = df_bord.groupby(['Categoría', 'OP Det']).agg({
    'Diferencia': 'sum',
    'Nombre del Comercial': 'first', 
    'Valor total OS': 'sum',
    'valor total op': 'sum'
}).reset_index()

df_consolidado_bord['abs_impacto'] = df_consolidado_bord['Diferencia'].abs()

# ... (tus pasos de top_sobrecosto, top_ahorro y concat se mantienen igual) ...
top_sobrecosto_bord = df_consolidado_bord.nlargest(10, 'Diferencia')
top_ahorro_bord = df_consolidado_bord.nsmallest(10, 'Diferencia')
top_impacto_bord = pd.concat([top_sobrecosto_bord, top_ahorro_bord], ignore_index=True)
top_impacto_bord = top_impacto_bord.sort_values(by='Diferencia', ascending=False)

top_impacto_bord['Etiqueta'] = top_impacto_bord['Categoría'] + " (OP: " + top_impacto_bord['OP Det'].astype(str) + ")"
top_impacto_bord['estado'] = top_impacto_bord['Diferencia'].apply(lambda x: 'Ahorro' if x < 0 else 'Sobrecosto')

# 2. Configuramos el gráfico con hover_data y labels
# 1. Asegúrate de que el hover_data tenga las 3 columnas en este orden exacto
fig_bord = px.bar(
    top_impacto_bord,
    x='Diferencia',
    y='Etiqueta',
    orientation='h',
    color='estado',
    color_discrete_map={'Ahorro': 'green', 'Sobrecosto': 'red'},
    hover_data=['Nombre del Comercial', 'Valor total OS', 'valor total op'], # [0], [1], [2]
    labels={
        "Nombre del Comercial": "Comercial",
        "Valor total OS": "Valor total pagado",
        "valor total op": "Valor total presupuestado",
        "Diferencia": "Desviación ($)"
    }
)

# 2. Ajustamos el template para que llame a cada dato por su posición
fig_bord.update_traces(
    marker_line_width=0,
    hovertemplate=(
        "<b>%{y}</b><br>" +
        "Diferencia: %{x:$,.0f}<br>" +
        "Comercial: %{customdata[0]}<br>" +
        "Pagado: %{customdata[1]:$,.0f}<br>" +
        "Costeado: %{customdata[2]:$,.0f}" + # <-- Agregamos el índice [2]
        "<extra></extra>"
    )
)
# Esto elimina las líneas negras que dividen los segmentos dentro de la barra
fig_bord.update_traces(marker_line_width=0) 

fig_bord.update_layout(
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
fig_bord.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1
)

fig_bord.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray'
)

# %% [markdown]
# ### Estampado

# %%
# Filtramos el DF para obtener solo los datos de Bordado.
df_est = df_costos[df_costos['Proceso Producción'] == 'Estampado'].copy()

# Definimos una columna de estado para tener el contexto de qué significa cada punto en la gráfica.
df_est['estado'] = df_est.apply(
    lambda 
    x: 'Ahorro' 
    if x['OS-Valor Unitario'] < x['costo_antes_iva'] 
    else 'Sobrecosto',
    axis=1
)

# Creamos la gráfica de bordado, lo que esta encima de la línea diagonal es ahorro y lo que esta debajo es sobrecosto
# El tamaño de cada punto representa el impacto económico

fig_estampado= px.scatter(
    df_est,
    x='OS-Valor Unitario',
    y='costo_antes_iva',
    color='Categoría',
    color_discrete_sequence=paleta_textil,
    hover_data=['OP Det', 'Nombre del Comercial', 'Costeo_Producto', 'OS-Valor Unitario', 'costo_antes_iva'],
    title='Estampado',
)

min_val = min(df_est['costo_antes_iva'].min(), df_est['OS-Valor Unitario'].min())
max_val = max(df_est['costo_antes_iva'].max(), df_est['OS-Valor Unitario'].max())

fig_estampado.add_shape(
    type="line",
    x0=min_val, y0=min_val,
    x1=max_val, y1=max_val,
    line=dict(color="pink", dash="dash")
)

fig_estampado.update_traces(marker=dict(size=5)) 

fig_estampado.update_layout(
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
fig_estampado.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1,
    title='Costo OS antes IVA'
)

fig_estampado.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray',
    title='Costo antes IVA (costeado)'
)

# %%
df_est = df_costos[df_costos['Proceso Producción'] == 'Estampado']

# Sumamos la diferencia por OP para que solo exista una barra por etiqueta
df_consolidado_est = df_est.groupby(['Categoría', 'OP Det']).agg({
    'Diferencia': 'sum',
    'Nombre del Comercial': 'first', 
    'Valor total OS': 'sum',
    'valor total op': 'sum'
}).reset_index()

df_consolidado_est['abs_impacto'] = df_consolidado_est['Diferencia'].abs()

# ... (tus pasos de top_sobrecosto, top_ahorro y concat se mantienen igual) ...
top_sobrecosto_est = df_consolidado_est.nlargest(10, 'Diferencia')
top_ahorro_est = df_consolidado_est.nsmallest(10, 'Diferencia')
top_impacto_est = pd.concat([top_sobrecosto_est, top_ahorro_est], ignore_index=True)
top_impacto_est = top_impacto_est.sort_values(by='Diferencia', ascending=False)

top_impacto_est['Etiqueta'] = top_impacto_est['Categoría'] + " (OP: " + top_impacto_est['OP Det'].astype(str) + ")"
top_impacto_est['estado'] = top_impacto_est['Diferencia'].apply(lambda x: 'Ahorro' if x < 0 else 'Sobrecosto')

fig_est = px.bar(
    top_impacto_est,
    x='Diferencia',
    y='Etiqueta',
    orientation='h',
    color='estado',
    color_discrete_map={'Ahorro': 'green', 'Sobrecosto': 'red'},
    hover_data=['Nombre del Comercial', 'Valor total OS', 'valor total op'], # [0], [1], [2]
    labels={
        "Nombre del Comercial": "Comercial",
        "Valor total OS": "Valor total pagado",
        "valor total op": "Valor total presupuestado",
        "Diferencia": "Desviación ($)"
    }
)

# 2. Ajustamos el template para que llame a cada dato por su posición
fig_est.update_traces(
    marker_line_width=0,
    hovertemplate=(
        "<b>%{y}</b><br>" +
        "Diferencia: %{x:$,.0f}<br>" +
        "Comercial: %{customdata[0]}<br>" +
        "Pagado: %{customdata[1]:$,.0f}<br>" +
        "Costeado: %{customdata[2]:$,.0f}" + # <-- Agregamos el índice [2]
        "<extra></extra>"
    )
)

# Esto elimina las líneas negras que dividen los segmentos dentro de la barra
fig_est.update_traces(marker_line_width=0) 

fig_est.update_layout(
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
fig_est.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1
)

fig_est.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray'
)

# %% [markdown]
# ### Paquete Completo Sin Marca

# %%
# Filtramos el DF para obtener solo los datos de Bordado.
df_pqt_sin = df_costos[df_costos['Proceso Producción'] == 'Paquete Completo Sin Marca'].copy()

# Definimos una columna de estado para tener el contexto de qué significa cada punto en la gráfica.
df_pqt_sin['estado'] = df_pqt_sin.apply(
    lambda 
    x: 'Ahorro' 
    if x['OS-Valor Unitario'] < x['costo_antes_iva'] 
    else 'Sobrecosto',
    axis=1
)

# Creamos la gráfica de bordado, lo que esta encima de la línea diagonal es ahorro y lo que esta debajo es sobrecosto
# El tamaño de cada punto representa el impacto económico

fig_pqt_sin= px.scatter(
    df_pqt_sin,
    x='OS-Valor Unitario',
    y='costo_antes_iva',
    color='Categoría',
    color_discrete_sequence=paleta_textil,
    hover_data=['OP Det', 'Nombre del Comercial', 'Costeo_Producto', 'OS-Valor Unitario', 'costo_antes_iva'],
    title='Paquete Completo Sin Marca',
)

min_val = min(df_pqt_sin['costo_antes_iva'].min(), df_pqt_sin['OS-Valor Unitario'].min())
max_val = max(df_pqt_sin['costo_antes_iva'].max(), df_pqt_sin['OS-Valor Unitario'].max())

fig_pqt_sin.add_shape(
    type="line",
    x0=min_val, y0=min_val,
    x1=max_val, y1=max_val,
    line=dict(color="pink", dash="dash")
)

fig_pqt_sin.update_traces(marker=dict(size=15)) 

fig_pqt_sin.update_layout(
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
fig_pqt_sin.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1,
    title='Costo OS antes IVA'
)

fig_pqt_sin.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray',
    title='Costo antes IVA (costeado)'
)

# %%
# Solo creamos la columna de estado para el color del gráfico
df_costos['estado'] = df_costos['Diferencia'].apply(
    lambda x: 'Ahorro' if x < 0 else 'Sobrecosto'
)

df_pqt_sin = df_costos[df_costos['Proceso Producción'] == 'Paquete Completo Sin Marca']

# Sumamos la diferencia por OP para que solo exista una barra por etiqueta
df_consolidado_pqsin = df_pqt_sin.groupby(['Categoría', 'OP Det']).agg({
    'Diferencia': 'sum'
}).reset_index()

# Ahora sí calculamos el impacto absoluto sobre el total de la OP
df_consolidado_pqsin['abs_impacto'] = df_consolidado_pqsin['Diferencia'].abs()

top_sobrecosto_pqtsin = df_consolidado_pqsin.nlargest(10, 'Diferencia')
top_ahorro_pqtsin= df_consolidado_pqsin.nsmallest(10, 'Diferencia')

# Unir ambos
top_impacto_pqsin = pd.concat([top_sobrecosto_pqtsin, top_ahorro_pqtsin], ignore_index=True)

# Ordenar de mayor a menor Diferencia (rojo arriba, verde abajo)
top_impacto_pqsin = top_impacto_pqsin.sort_values(by='Diferencia', ascending=False)

top_impacto_pqsin['Etiqueta'] = top_impacto_pqsin['Categoría'] + " (OP: " + top_impacto_pqsin['OP Det'].astype(str) + ")"

top_impacto_pqsin['estado'] = top_impacto_pqsin['Diferencia'].apply(
    lambda x: 'Ahorro' if x < 0 else 'Sobrecosto'
)

fig_pqt_sinM = px.bar(
    top_impacto_pqsin,
    x='Diferencia',
    y='Etiqueta',
    orientation='h',
    color='estado',
    color_discrete_map={'Ahorro': 'green', 'Sobrecosto': 'red'},
    template='plotly_dark'
)

# Esto elimina las líneas negras que dividen los segmentos dentro de la barra
fig_pqt_sinM.update_traces(marker_line_width=0) 

fig_pqt_sinM.update_layout(
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
fig_pqt_sinM.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1
)

fig_pqt_sinM.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray'
)

# %% [markdown]
# ### Prelavado

# %%
df_prelavado = df_costos[df_costos['Proceso Producción'] == 'Prelavado'].copy()

# Definimos una columna de estado para tener el contexto de qué significa cada punto en la gráfica.
df_prelavado['estado'] = df_prelavado.apply(
    lambda 
    x: 'Ahorro' 
    if x['OS-Valor Unitario'] < x['costo_antes_iva'] 
    else 'Sobrecosto',
    axis=1
)

# Creamos la gráfica de bordado, lo que esta encima de la línea diagonal es ahorro y lo que esta debajo es sobrecosto
# El tamaño de cada punto representa el impacto económico

fig_pre= px.scatter(
    df_prelavado,
    x='OS-Valor Unitario',
    y='costo_antes_iva',
    color='Categoría',
    color_discrete_sequence=paleta_textil,
    hover_data=['OP Det', 'Nombre del Comercial', 'Costeo_Producto', 'OS-Valor Unitario', 'costo_antes_iva'],
    title='Prelavado',
)

min_val = min(df_prelavado['costo_antes_iva'].min(), df_prelavado['OS-Valor Unitario'].min())
max_val = max(df_prelavado['costo_antes_iva'].max(), df_prelavado['OS-Valor Unitario'].max())

fig_pre.add_shape(
    type="line",
    x0=min_val, y0=min_val,
    x1=max_val, y1=max_val,
    line=dict(color="pink", dash="dash")
)

fig_pre.update_traces(marker=dict(size=15)) 

fig_pre.update_layout(
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
fig_pre.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1,
    title='Costo OS antes IVA'
)

fig_pre.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray',
    title='Costo antes IVA (costeado)'
)

# %%
df_pre = df_costos[df_costos['Proceso Producción'] == 'Prelavado']

# Sumamos la diferencia por OP para que solo exista una barra por etiqueta
df_consolidado_pre = df_pre.groupby(['Categoría', 'OP Det']).agg({
    'Diferencia': 'sum'
}).reset_index()

# Ahora sí calculamos el impacto absoluto sobre el total de la OP
df_consolidado_pre['abs_impacto'] = df_consolidado_pre['Diferencia'].abs()

# Top 10 de las OPs con mayor impacto real
top_sobrecosto_pre = df_consolidado_pre.nlargest(10, 'Diferencia')
top_ahorro_pre = df_consolidado_pre.nsmallest(10, 'Diferencia')

# Unir ambos
top_impacto_pre = pd.concat([top_sobrecosto_pre, top_ahorro_pre], ignore_index=True)

# Ordenar de mayor a menor Diferencia (rojo arriba, verde abajo)
top_impacto_pre = top_impacto_pre.sort_values(by='Diferencia', ascending=False)

top_impacto_pre['Etiqueta'] = top_impacto_pre['Categoría'] + " (OP: " + top_impacto_pre['OP Det'].astype(str) + ")"

top_impacto_pre['estado'] = top_impacto_pre['Diferencia'].apply(
    lambda x: 'Ahorro' if x < 0 else 'Sobrecosto'
)

fig_prelavado = px.bar(
    top_impacto_pre,
    x='Diferencia',
    y='Etiqueta',
    orientation='h',
    color='estado',
    color_discrete_map={'Ahorro': 'green', 'Sobrecosto': 'red'},
    template='plotly_dark'
)

# Esto elimina las líneas negras que dividen los segmentos dentro de la barra
fig_prelavado.update_traces(marker_line_width=0) 

fig_prelavado.update_layout(
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
fig_prelavado.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1
)

fig_prelavado.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray'
)
# %% [markdown]
# ### Corte y Confeccion

# %%
df_cyc = df_costos[df_costos['Proceso Producción'] == 'Corte y Confeccion'].copy()

# Definimos una columna de estado para tener el contexto de qué significa cada punto en la gráfica.
df_cyc['estado'] = df_cyc.apply(
    lambda 
    x: 'Ahorro' 
    if x['OS-Valor Unitario'] < x['costo_antes_iva'] 
    else 'Sobrecosto',
    axis=1
)

# Creamos la gráfica de bordado, lo que esta encima de la línea diagonal es ahorro y lo que esta debajo es sobrecosto
# El tamaño de cada punto representa el impacto económico

fig_cyc= px.scatter(
    df_cyc,
    x='OS-Valor Unitario',
    y='costo_antes_iva',
    color='Categoría',
    color_discrete_sequence=paleta_textil,
    hover_data=['OP Det', 'Nombre del Comercial', 'Costeo_Producto', 'OS-Valor Unitario', 'costo_antes_iva'],
    title='Corte y Confección',
)

min_val = min(df_cyc['costo_antes_iva'].min(), df_cyc['OS-Valor Unitario'].min())
max_val = max(df_cyc['costo_antes_iva'].max(), df_cyc['OS-Valor Unitario'].max())

fig_cyc.add_shape(
    type="line",
    x0=min_val, y0=min_val,
    x1=max_val, y1=max_val,
    line=dict(color="pink", dash="dash")
)

fig_cyc.update_traces(marker=dict(size=15)) 

fig_cyc.update_layout(
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
fig_cyc.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1,
    title='Costo OS antes IVA'
)

fig_cyc.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray',
    title='Costo antes IVA (costeado)'
)

# %%
df_cycc = df_costos[df_costos['Proceso Producción'] == 'Corte y Confeccion']

# Sumamos la diferencia por OP para que solo exista una barra por etiqueta
df_consolidado_cyc = df_cycc.groupby(['Categoría', 'OP Det']).agg({
    'Diferencia': 'sum'
}).reset_index()

# Ahora sí calculamos el impacto absoluto sobre el total de la OP
df_consolidado_cyc['abs_impacto'] = df_consolidado_cyc['Diferencia'].abs()

top_sobrecosto_cyc = df_consolidado_cyc.nlargest(10, 'Diferencia')
top_ahorro_cyc = df_consolidado_cyc.nsmallest(10, 'Diferencia')

# Unir ambos
top_impacto_cyc = pd.concat([top_sobrecosto_cyc, top_ahorro_cyc], ignore_index=True)

# Ordenar de mayor a menor Diferencia (rojo arriba, verde abajo)
top_impacto_cyc = top_impacto_cyc.sort_values(by='Diferencia', ascending=False)

top_impacto_cyc['Etiqueta'] = top_impacto_cyc['Categoría'] + " (OP: " + top_impacto_cyc['OP Det'].astype(str) + ")"

top_impacto_cyc['estado'] = top_impacto_cyc['Diferencia'].apply(
    lambda x: 'Ahorro' if x < 0 else 'Sobrecosto'
)


fig_cycc = px.bar(
    top_impacto_cyc,
    x='Diferencia',
    y='Etiqueta',
    orientation='h',
    color='estado',
    color_discrete_map={'Ahorro': 'green', 'Sobrecosto': 'red'},
    template='plotly_dark'
)

# Esto elimina las líneas negras que dividen los segmentos dentro de la barra
fig_cycc.update_traces(marker_line_width=0) 

fig_cycc.update_layout(
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
fig_cycc.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1
)

fig_cycc.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray'
)
fig_cycc.update_xaxes(tickformat='.2s')


# %% [markdown]
# ### Paquete Completo

# %%
df_pqt_com = df_costos[df_costos['Proceso Producción'] == 'Paquete Completo'].copy()

# Definimos una columna de estado para tener el contexto de qué significa cada punto en la gráfica.
df_pqt_com['estado'] = df_pqt_com.apply(
    lambda 
    x: 'Ahorro' 
    if x['OS-Valor Unitario'] < x['costo_antes_iva'] 
    else 'Sobrecosto',
    axis=1
)

# Creamos la gráfica de bordado, lo que esta encima de la línea diagonal es ahorro y lo que esta debajo es sobrecosto
# El tamaño de cada punto representa el impacto económico

fig_pqt_com= px.scatter(
    df_pqt_com,
    x='OS-Valor Unitario',
    y='costo_antes_iva',
    color='Categoría',
    color_discrete_sequence=paleta_textil,
    hover_data=['OP Det', 'Nombre del Comercial', 'Costeo_Producto', 'OS-Valor Unitario', 'costo_antes_iva'],
    title='Paquete Completo',
)

min_val = min(df_pqt_com['costo_antes_iva'].min(), df_pqt_com['OS-Valor Unitario'].min())
max_val = max(df_pqt_com['costo_antes_iva'].max(), df_pqt_com['OS-Valor Unitario'].max())

fig_pqt_com.add_shape(
    type="line",
    x0=min_val, y0=min_val,
    x1=max_val, y1=max_val,
    line=dict(color="pink", dash="dash")
)

fig_pqt_com.update_traces(marker=dict(size=15)) 

fig_pqt_com.update_layout(
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
fig_pqt_com.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1,
    title='Costo OS antes IVA'
)

fig_pqt_com.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray',
    title='Costo antes IVA (costeado)'
)

# %%

df_pqtcom = df_costos[df_costos['Proceso Producción'] == 'Paquete Completo']

# Sumamos la diferencia por OP para que solo exista una barra por etiqueta
df_consolidado_pqtcom = df_pqtcom.groupby(['Categoría', 'OP Det']).agg({
    'Diferencia': 'sum'
}).reset_index()

# Ahora sí calculamos el impacto absoluto sobre el total de la OP
df_consolidado_pqtcom['abs_impacto'] = df_consolidado_pqtcom['Diferencia'].abs()

top_sobrecosto_pqtcom = df_consolidado_pqtcom.nlargest(10, 'Diferencia')
top_ahorro_pqtcom = df_consolidado_pqtcom.nsmallest(10, 'Diferencia')

# Unir ambos
top_impacto_pqtcom = pd.concat([top_sobrecosto_pqtcom, top_ahorro_pqtcom], ignore_index=True)

# Ordenar de mayor a menor Diferencia (rojo arriba, verde abajo)
top_impacto_pqtcom = top_impacto_pqtcom.sort_values(by='Diferencia', ascending=False)

top_impacto_pqtcom['Etiqueta'] = top_impacto_pqtcom['Categoría'] + " (OP: " + top_impacto_pqtcom['OP Det'].astype(str) + ")"

top_impacto_pqtcom['estado'] = top_impacto_pqtcom['Diferencia'].apply(
    lambda x: 'Ahorro' if x < 0 else 'Sobrecosto'
)


fig_pqtcom = px.bar(
    top_impacto_pqtcom,
    x='Diferencia',
    y='Etiqueta',
    orientation='h',
    color='estado',
    color_discrete_map={'Ahorro': 'green', 'Sobrecosto': 'red'},
    template='plotly_dark'
)

# Esto elimina las líneas negras que dividen los segmentos dentro de la barra
fig_pqtcom.update_traces(marker_line_width=0) 

fig_pqtcom.update_layout(
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
fig_pqtcom.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1
)

fig_pqtcom.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray'
)


# %% [markdown]
# ## Impacto por comercial

# %% [markdown]
# ### Confección

# %%
# Filtramos por proceso de confección
df_confeccion = df_costos[df_costos['Proceso Producción'] == "Confección"]
df_confeccion['Tarea'] = df_confeccion['Categoría'].astype(str) + " (" + df_confeccion['Proceso Producción'].astype(str) + ")"


# Identificamos las tareas más costosas en el proceso de confección
top5_tareas = (df_confeccion.groupby('Tarea')['Diferencia']
               .apply(lambda x: x.abs().sum())  # suma de absolutos, no absoluto de la suma
               .sort_values(ascending=False)
               .head(8)
               .index.tolist())

df_plot = df_confeccion[df_confeccion['Tarea'].isin(top5_tareas)]

# Agrupamos por tarea (categoría + proceso) y por comercial, calculamos el promedio del costeo de cada uno
df_comparativa = df_plot.groupby(['Tarea', 'Nombre del Comercial'])['Diferencia'].mean().reset_index()
df_referencia = df_plot.groupby('Tarea')['Diferencia'].mean().reset_index()

# Hacemos la gráfica de barras del proceso de confección
fig_conf_comercial = px.bar(df_comparativa, 
             x='Diferencia', 
             y='Tarea', 
             color='Nombre del Comercial',
             barmode='group',
             orientation='h',
             text_auto='.0f',
             title='Confección',
             color_discrete_sequence=px.colors.qualitative.Bold)

fig_conf_comercial.update_layout(xaxis_title="Costo Promedio ($)", yaxis_title="", showlegend=True)

fig_conf_comercial.update_layout(
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
fig_conf_comercial.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1
)

fig_conf_comercial.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray'
)

# %% [markdown]
# ### Bordado

# %%
# Filtramos por proceso de confección
df_bordado = df_costos[df_costos['Proceso Producción'] == "Bordado"]
df_bordado['Tarea'] = df_bordado['Categoría'].astype(str) + " (" + df_bordado['Proceso Producción'].astype(str) + ")"

# Identificamos las tareas más costosas en el proceso de confección
top5_tareas = (df_bordado.groupby('Tarea')['Diferencia valor unitario']
               .apply(lambda x: x.abs().sum())  # suma de absolutos, no absoluto de la suma
               .sort_values(ascending=False)
               .head(8)
               .index.tolist())

df_plot = df_bordado[df_bordado['Tarea'].isin(top5_tareas)]

# Agrupamos por tarea (categoría + proceso) y por comercial, calculamos el promedio del costeo de cada uno
df_comparativa_bordado = df_plot.groupby(['Tarea', 'Nombre del Comercial'])['Diferencia valor unitario'].mean().reset_index()
df_referencia_bordado = df_plot.groupby('Tarea')['Diferencia valor unitario'].mean().reset_index()

# Hacemos la gráfica de barras del proceso de confección
fig_bordado_comercial = px.bar(df_comparativa_bordado, 
             x='Diferencia valor unitario', 
             y='Tarea', 
             color='Nombre del Comercial',
             barmode='group',
             orientation='h',
             text_auto='.0f',
             title='Confección',
             color_discrete_sequence=px.colors.qualitative.Bold)

fig_bordado_comercial.update_layout(xaxis_title="Costo Promedio ($)", yaxis_title="", showlegend=True)

fig_bordado_comercial.update_layout(
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
fig_bordado_comercial.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1
)

fig_bordado_comercial.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray'
)

# %% [markdown]
# ### Sublimación

# %%
# Filtramos por proceso de confección
df_sublimacion = df_costos[df_costos['Proceso Producción'] == 'Sublimación']
df_sublimacion['Tarea'] = df_sublimacion['Categoría'].astype(str) + " (" + df_sublimacion['Proceso Producción'].astype(str) + ")"

# Identificamos las tareas más costosas en el proceso de confección
top5_tareas = (df_sublimacion.groupby('Tarea')['Diferencia valor unitario']
               .apply(lambda x: x.abs().sum())  # suma de absolutos, no absoluto de la suma
               .sort_values(ascending=False)
               .head(8)
               .index.tolist())

df_plot_sublimacion = df_sublimacion[df_sublimacion['Tarea'].isin(top5_tareas)]

# Agrupamos por tarea (categoría + proceso) y por comercial, calculamos el promedio del costeo de cada uno
df_comparativa_sublimacion = df_plot_sublimacion.groupby(['Tarea', 'Nombre del Comercial'])['Diferencia valor unitario'].mean().reset_index()
df_referencia_sublimacion = df_plot_sublimacion.groupby('Tarea')['Diferencia valor unitario'].mean().reset_index()

# Hacemos la gráfica de barras del proceso de confección
fig_sublimacion_comercial = px.bar(df_comparativa_sublimacion, 
             x='Diferencia valor unitario', 
             y='Tarea', 
             color='Nombre del Comercial',
             barmode='group',
             orientation='h',
             text_auto='.0f',
             title='Sublimación',
             color_discrete_sequence=px.colors.qualitative.Bold)

fig_sublimacion_comercial.update_layout(xaxis_title="Costo Promedio ($)", yaxis_title="", showlegend=True)

fig_sublimacion_comercial.update_layout(
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
fig_sublimacion_comercial.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1
)

fig_sublimacion_comercial.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray'
)

# %% [markdown]
# ### Estampado

# %%
df_estampado = df_costos[df_costos['Proceso Producción'] == 'Estampado']
df_estampado['Tarea'] = df_estampado['Categoría'].astype(str) + " (" + df_estampado['Proceso Producción'].astype(str) + ")"


# Identificamos las tareas más costosas en el proceso de confección
top5_tareas = (df_estampado.groupby('Tarea')['Diferencia valor unitario']
               .apply(lambda x: x.abs().sum())  # suma de absolutos, no absoluto de la suma
               .sort_values(ascending=False)
               .head(8)
               .index.tolist())

df_plot_estampado = df_estampado[df_estampado['Tarea'].isin(top5_tareas)]

# Agrupamos por tarea (categoría + proceso) y por comercial, calculamos el promedio del costeo de cada uno
df_comparativa_estampado = df_plot_estampado.groupby(['Tarea', 'Nombre del Comercial'])['Diferencia valor unitario'].mean().reset_index()
df_referencia_estampado = df_plot_estampado.groupby('Tarea')['Diferencia valor unitario'].mean().reset_index()

# Hacemos la gráfica de barras del proceso de confección
fig_estampado_comercial = px.bar(df_comparativa_estampado, 
             x='Diferencia valor unitario', 
             y='Tarea', 
             color='Nombre del Comercial',
             barmode='group',
             orientation='h',
             text_auto='.0f',
             title='Estampado',
             color_discrete_sequence=px.colors.qualitative.Bold)

fig_estampado_comercial.update_layout(xaxis_title="Costo Promedio ($)", yaxis_title="", showlegend=True)

fig_estampado_comercial.update_layout(
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
fig_estampado_comercial.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1
)

fig_estampado_comercial.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray'
)

# %% [markdown]
# ### Paquete Completo Sin Marca

# %%
df_pqt_sin = df_costos[df_costos['Proceso Producción'] == 'Paquete Completo Sin Marca']
df_pqt_sin['Tarea'] = df_pqt_sin['Categoría'].astype(str) + " (" + df_pqt_sin['Proceso Producción'].astype(str) + ")"


# Identificamos las tareas más costosas en el proceso de confección
top5_tareas = (df_pqt_sin.groupby('Tarea')['Diferencia valor unitario']
               .apply(lambda x: x.abs().sum())  # suma de absolutos, no absoluto de la suma
               .sort_values(ascending=False)
               .head(8)
               .index.tolist())

df_plot_pqtsin = df_pqt_sin[df_pqt_sin['Tarea'].isin(top5_tareas)]

# Agrupamos por tarea (categoría + proceso) y por comercial, calculamos el promedio del costeo de cada uno
df_comparativa_pqtsin = df_plot_pqtsin.groupby(['Tarea', 'Nombre del Comercial'])['Diferencia valor unitario'].mean().reset_index()
df_referencia_pqtsin = df_plot_pqtsin.groupby('Tarea')['Diferencia valor unitario'].mean().reset_index()

# Hacemos la gráfica de barras del proceso de confección
fig_pqtsin_comercial = px.bar(df_comparativa_pqtsin, 
             x='Diferencia valor unitario', 
             y='Tarea', 
             color='Nombre del Comercial',
             barmode='group',
             orientation='h',
             text_auto='.0f',
             title='Paquete Completo Sin Marca',
             color_discrete_sequence=px.colors.qualitative.Bold)

fig_pqtsin_comercial.update_layout(xaxis_title="Costo Promedio ($)", yaxis_title="", showlegend=True)

fig_pqtsin_comercial.update_layout(
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
fig_pqtsin_comercial.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1
)

fig_pqtsin_comercial.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray'
)

# %% [markdown]
# ### Prelavado

# %%
df_prel = df_costos[df_costos['Proceso Producción'] == 'Prelavado']
df_prel['Tarea'] = df_prel['Categoría'].astype(str) + " (" + df_prel['Proceso Producción'].astype(str) + ")"

# Identificamos las tareas más costosas en el proceso de confección
top5_tareas = (df_prel.groupby('Tarea')['Diferencia valor unitario']
               .apply(lambda x: x.abs().sum())  # suma de absolutos, no absoluto de la suma
               .sort_values(ascending=False)
               .head(8)
               .index.tolist())

df_plot_prel = df_prel[df_prel['Tarea'].isin(top5_tareas)]

# Agrupamos por tarea (categoría + proceso) y por comercial, calculamos el promedio del costeo de cada uno
df_comparativa_prel = df_plot_prel.groupby(['Tarea', 'Nombre del Comercial'])['Diferencia valor unitario'].mean().reset_index()
df_referencia_prel = df_plot_prel.groupby('Tarea')['Diferencia valor unitario'].mean().reset_index()

# Hacemos la gráfica de barras del proceso de confección
fig_prelavado_comercial = px.bar(df_comparativa_prel, 
             x='Diferencia valor unitario', 
             y='Tarea', 
             color='Nombre del Comercial',
             barmode='group',
             orientation='h',
             text_auto='.0f',
             title='Paquete Completo Sin Marca',
             color_discrete_sequence=px.colors.qualitative.Bold)

fig_prelavado_comercial.update_layout(xaxis_title="Costo Promedio ($)", yaxis_title="", showlegend=True)

fig_prelavado_comercial.update_layout(
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
fig_prelavado_comercial.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1
)

fig_prelavado_comercial.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray'
)
# %% [markdown]
# ### Corte y Confeccion

# %%
df_cyc = df_costos[df_costos['Proceso Producción'] == 'Corte y Confeccion']
df_cyc['Tarea'] = df_cyc['Categoría'].astype(str) + " (" + df_cyc['Proceso Producción'].astype(str) + ")"


# Identificamos las tareas más costosas en el proceso de confección
top5_tareas = (df_cyc.groupby('Tarea')['Diferencia valor unitario']
               .apply(lambda x: x.abs().sum())  # suma de absolutos, no absoluto de la suma
               .sort_values(ascending=False)
               .head(8)
               .index.tolist())

df_plot_cyc = df_cyc[df_cyc['Tarea'].isin(top5_tareas)]

# Agrupamos por tarea (categoría + proceso) y por comercial, calculamos el promedio del costeo de cada uno
df_comparativa_cyc = df_plot_cyc.groupby(['Tarea', 'Nombre del Comercial'])['Diferencia valor unitario'].mean().reset_index()
df_referencia_cyc = df_plot_cyc.groupby('Tarea')['Diferencia valor unitario'].mean().reset_index()

# Hacemos la gráfica de barras del proceso de confección
fig_cyc_comercial = px.bar(df_comparativa_cyc, 
             x='Diferencia valor unitario', 
             y='Tarea', 
             color='Nombre del Comercial',
             barmode='group',
             orientation='h',
             text_auto='.0f',
             title='Paquete Completo Sin Marca',
             color_discrete_sequence=px.colors.qualitative.Bold)

fig_cyc_comercial.update_layout(xaxis_title="Costo Promedio ($)", yaxis_title="", showlegend=True)

fig_cyc_comercial.update_layout(
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
fig_cyc_comercial.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1
)

fig_cyc_comercial.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray'
)

# %% [markdown]
# ### Paquete Completo

# %%
df_pqtcom = df_costos[df_costos['Proceso Producción'] == 'Paquete Completo']
df_pqtcom['Tarea'] = df_pqtcom['Categoría'].astype(str) + " (" + df_pqtcom['Proceso Producción'].astype(str) + ")"


# Identificamos las tareas más costosas en el proceso de confección
top5_tareas = (df_pqtcom.groupby('Tarea')['Diferencia valor unitario']
               .apply(lambda x: x.abs().sum())  # suma de absolutos, no absoluto de la suma
               .sort_values(ascending=False)
               .head(8)
               .index.tolist())

df_plot_pqtcom = df_pqtcom[df_pqtcom['Tarea'].isin(top5_tareas)]

# Agrupamos por tarea (categoría + proceso) y por comercial, calculamos el promedio del costeo de cada uno
df_comparativa_pqtcom = df_plot_pqtcom.groupby(['Tarea', 'Nombre del Comercial'])['Diferencia valor unitario'].mean().reset_index()
df_referencia_pqtcom = df_plot_pqtcom.groupby('Tarea')['Diferencia valor unitario'].mean().reset_index()

# Hacemos la gráfica de barras del proceso de confección
fig_pqtc_comercial = px.bar(df_comparativa_pqtcom, 
             x='Diferencia valor unitario', 
             y='Tarea', 
             color='Nombre del Comercial',
             barmode='group',
             orientation='h',
             text_auto='.0f',
             title='Paquete Completo Sin Marca',
             color_discrete_sequence=px.colors.qualitative.Bold)

fig_pqtc_comercial.update_layout(xaxis_title="Costo Promedio ($)", yaxis_title="", showlegend=True)

fig_pqtc_comercial.update_layout(
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
fig_pqtc_comercial.update_xaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', # Un gris más marcado (puedes usar 'gray' si lo quieres aún más oscuro)
    linecolor='gray',    # Línea del eje principal en negro
    zeroline=True,        # Mantener la línea del cero...
    zerolinecolor='#d3d3d3', # ...pero usar un gris mucho más suave (LightGrey)
    zerolinewidth=1
)

fig_pqtc_comercial.update_yaxes(
    showgrid=True, 
    gridwidth=1, 
    gridcolor='#bdbdbd', 
    linecolor='gray'
)



# %%
# Filtro de fecha para tomar exactamente un año 
df_filtrado_pro = df_costos_valorop[df_costos_valorop['Fecha'] >= '2025-03-17'].copy()

# hacemos la agrupación para el gráfico
df_pareto_volu = df_filtrado_pro.groupby('OS-Proveedor').agg({
    'OS-Cantidad': 'sum',
    'Valor total OS': 'sum'
}).reset_index()

# Ordenamos la cantidad de mayor a menor
df_pareto_volu = df_pareto_volu.sort_values(by='OS-Cantidad', ascending=False)

# Cálculo de acumulados sobre el VOLUMEN de producción
total_prendas = df_pareto_volu['OS-Cantidad'].sum()
df_pareto_volu['Porcentaje'] = (df_pareto_volu['OS-Cantidad'] / total_prendas) * 100
df_pareto_volu['Acumulado'] = df_pareto_volu['Porcentaje'].cumsum()

fig_vol = go.Figure()

# Barras de la cantidad de pedidos por cliente

fig_vol.add_trace(go.Bar(
    x=df_pareto_volu['OS-Proveedor'],
    y=df_pareto_volu['OS-Cantidad'],
    name='Volumen de Producción (Prendas)',
    marker_color="#632E8B", 
    # Pasamos datos extra al hover/etiqueta
    customdata=df_pareto_volu[['Valor total OS']], 
    hovertemplate=( 
        "<b>Proveedor: %{x}</b><br>" +
        "Cantidad de Prendas: %{y:,.0f}<br><br>" +
        "Valor total de OS: %{customdata[0]:$,.0f}<br>"
        "<extra></extra>"
    )
))

# Línea del % acumulado
fig_vol.add_trace(go.Scatter(
    x=df_pareto_volu['OS-Proveedor'],
    y=df_pareto_volu['Acumulado'],
    name='% Acumulado Volumen',
    yaxis='y2',
    line=dict(color="#4DEBBE", width=3),
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

#%%
df_filtrado_prov = df_costos_fechacom[df_costos_fechacom['Fecha'] >= '2025-03-17'].copy()

# Agrupar por CLIENTE para el Pareto
df_pareto_valorpro = df_filtrado_prov.groupby('OS-Proveedor').agg({
    'OS-Cantidad': 'sum',
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
    x=df_pareto_valorpro['OS-Proveedor'],
    y=df_pareto_valorpro['Valor total OS'],
    name='Valor Total OS ($)',
    marker_color='#632E8B', 
    customdata=df_pareto_valorpro[['OS-Cantidad']], 
    hovertemplate=(
        "<b>Proveedor: %{x}</b><br>" +
        "Valor Total OS: %{y:$,.0f}<br>" +
        "Total Prendas: %{customdata[0]:,.0f}<br>" + # <--- Cambio aquí: :.0f elimina decimales
        "<extra></extra>"
    )
))

# Línea: % Acumulado
fig_valor_pro.add_trace(go.Scatter(
    x=df_pareto_valorpro['OS-Proveedor'],
    y=df_pareto_valorpro['Acumulado'],
    name='% Acumulado',
    yaxis='y2',
    line=dict(color="#4DEBBE", width=3),
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
