import streamlit as st
import pandas as pd
import time
from datetime import datetime
from io import BytesIO

def pedir_probabilidades(nombre):
    st.sidebar.markdown(f"### Probabilidades para {nombre}")
    col1, col2 = st.sidebar.columns(2)
    prob1 = col1.number_input(f"Prob. Escenario 1 ({nombre})", 0.0, 1.0, 0.5, 0.01, key=f"{nombre}_prob1")
    prob2 = col2.number_input(f"Prob. Escenario 2 ({nombre})", 0.0, 1.0, 0.5, 0.01, key=f"{nombre}_prob2")
    
    if abs((prob1 + prob2) - 1.0) > 1e-6:
        st.sidebar.error("⚠️ Las probabilidades deben sumar 1.0")
        return None, None
    return prob1, prob2

def calcular_vme_opcion_a(unidades_a1, precio_a1, prob_a1, unidades_a2, precio_a2, prob_a2):
    ingresos_a1 = unidades_a1 * precio_a1
    ingresos_a2 = unidades_a2 * precio_a2
    vme_a = (ingresos_a1 * prob_a1) + (ingresos_a2 * prob_a2)
    return ingresos_a1, ingresos_a2, vme_a

def calcular_vme_opcion_b(unidades_b1, precio_b1, prob_b1, unidades_b2, precio_b2, prob_b2, costo_estudio):
    ingresos_brutos_b1 = unidades_b1 * precio_b1
    ingresos_netos_b1 = ingresos_brutos_b1 - costo_estudio
    ingresos_brutos_b2 = unidades_b2 * precio_b2
    ingresos_netos_b2 = ingresos_brutos_b2 - costo_estudio
    vme_b = (ingresos_netos_b1 * prob_b1) + (ingresos_netos_b2 * prob_b2)
    return ingresos_netos_b1, ingresos_netos_b2, vme_b

def mostrar_resultados(nombre_opcion, ingreso1, prob1, ingreso2, prob2, vme, costo_estudio=None):
    st.subheader(f"📊 {nombre_opcion}")
    
    data = {
        "Escenario": [1, 2],
        "Probabilidad": [prob1, prob2],
        "Ingresos ($)": [ingreso1, ingreso2]
    }
    
    if costo_estudio is not None:
        data["Costo Estudio ($)"] = [costo_estudio, costo_estudio]
        data["Ingresos Netos ($)"] = [ingreso1, ingreso2]
    
    df = pd.DataFrame(data)
    st.dataframe(
        df.style.format({
            "Probabilidad": "{:.2%}",
            "Ingresos ($)": "${:,.2f}",
            "Costo Estudio ($)": "${:,.2f}",
            "Ingresos Netos ($)": "${:,.2f}"
        }),
        hide_index=True,
        use_container_width=True
    )
    
    st.metric(f"VME {nombre_opcion}", f"${vme:,.2f}")

def main():
    # Configuración de la página
    st.set_page_config(
        page_title="Calculador VME Pro",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📊 Calculador Avanzado de VME")
    
    with st.expander("ℹ️ Instrucciones y Guía Rápida", expanded=False):
        st.markdown("""
        ### Guía de Uso:
        1. **Configuración**: Ajusta los parámetros en el panel izquierdo
        2. **Probabilidades**: Deben sumar exactamente 1.0 (100%)
        3. **Resultados**: Se calculan y actualizan automáticamente
        4. **Exportación**: Puedes descargar los resultados en diferentes formatos
        """)
    
    # Valores por defecto con tipos explícitos
    DEFAULT_VALUES = {
        "unidades_a1": 100000,   # int
        "unidades_a2": 75000,    # int
        "unidades_b1": 75000,    # int
        "unidades_b2": 70000,    # int
        "precio_a1": 550.0,      # float
        "precio_a2": 550.0,      # float
        "precio_b1": 750.0,      # float
        "precio_b2": 750.0,      # float
        "prob_a1": 0.6,          # float
        "prob_a2": 0.4,          # float
        "prob_b1": 0.7,          # float
        "prob_b2": 0.3,          # float
        "costo_estudio": 100000.0 # float
    }
    
    # Panel de configuración
    with st.sidebar:
        st.header("⚙️ Configuración")
        personalizar = st.toggle("Modo Personalizado", True)
        
        if personalizar:
            st.subheader("🔧 Parámetros Opción (b)")
            col1, col2 = st.columns(2)
            unidades_a1 = col1.number_input(
                "Unidades Esc. 1 (b)", 
                min_value=0, 
                value=DEFAULT_VALUES["unidades_a1"], 
                step=1000,
                key="unidades_a1"
            )
            precio_a1 = col2.number_input(
                "Precio unitario ($)", 
                min_value=0.0, 
                value=float(DEFAULT_VALUES["precio_a1"]), 
                step=1.0, 
                format="%.2f", 
                key="precio_a1"
            )
            
            col3, col4 = st.columns(2)
            unidades_a2 = col3.number_input(
                "Unidades Esc. 2 (b)", 
                min_value=0, 
                value=DEFAULT_VALUES["unidades_a2"], 
                key="unidades_a2"
            )
            precio_a2 = col4.number_input(
                "Precio unitario ($)", 
                min_value=0.0, 
                value=float(DEFAULT_VALUES["precio_a2"]), 
                step=1.0, 
                format="%.2f", 
                key="precio_a2"
            )
            
            prob_result = pedir_probabilidades("Opción b")
            if prob_result[0] is not None:
                prob_a1, prob_a2 = prob_result
            else:
                prob_a1, prob_a2 = DEFAULT_VALUES["prob_a1"], DEFAULT_VALUES["prob_a2"]
            
            st.subheader("🔧 Parámetros Opción (c)")
            col5, col6 = st.columns(2)
            unidades_b1 = col5.number_input(
                "Unidades Esc. 1 (c)", 
                min_value=0, 
                value=DEFAULT_VALUES["unidades_b1"], 
                key="unidades_b1"
            )
            precio_b1 = col6.number_input(
                "Precio unitario ($)", 
                min_value=0.0, 
                value=float(DEFAULT_VALUES["precio_b1"]), 
                step=1.0, 
                format="%.2f", 
                key="precio_b1"
            )
            
            col7, col8 = st.columns(2)
            unidades_b2 = col7.number_input(
                "Unidades Esc. 2 (c)", 
                min_value=0, 
                value=DEFAULT_VALUES["unidades_b2"], 
                key="unidades_b2"
            )
            precio_b2 = col8.number_input(
                "Precio unitario ($)", 
                min_value=0.0, 
                value=float(DEFAULT_VALUES["precio_b2"]), 
                step=1.0, 
                format="%.2f", 
                key="precio_b2"
            )
            
            costo_estudio = st.number_input(
                "Costo estudio ($)", 
                min_value=0.0, 
                value=float(DEFAULT_VALUES["costo_estudio"]), 
                step=1000.0, 
                format="%.2f", 
                key="costo_estudio"
            )
            
            prob_result = pedir_probabilidades("Opción c")
            if prob_result[0] is not None:
                prob_b1, prob_b2 = prob_result
            else:
                prob_b1, prob_b2 = DEFAULT_VALUES["prob_b1"], DEFAULT_VALUES["prob_b2"]
        else:
            # Usar valores por defecto
            unidades_a1, unidades_a2 = DEFAULT_VALUES["unidades_a1"], DEFAULT_VALUES["unidades_a2"]
            precio_a1, precio_a2 = DEFAULT_VALUES["precio_a1"], DEFAULT_VALUES["precio_a2"]
            prob_a1, prob_a2 = DEFAULT_VALUES["prob_a1"], DEFAULT_VALUES["prob_a2"]
            
            unidades_b1, unidades_b2 = DEFAULT_VALUES["unidades_b1"], DEFAULT_VALUES["unidades_b2"]
            precio_b1, precio_b2 = DEFAULT_VALUES["precio_b1"], DEFAULT_VALUES["precio_b2"]
            prob_b1, prob_b2 = DEFAULT_VALUES["prob_b1"], DEFAULT_VALUES["prob_b2"]
            costo_estudio = DEFAULT_VALUES["costo_estudio"]
    
    # Validación final
    if None in [prob_a1, prob_a2, prob_b1, prob_b2]:
        st.warning("⚠️ Por favor ajusta las probabilidades para que sumen 1.0 en ambas opciones")
        st.stop()
    
    # Cálculos
    with st.spinner("Calculando VME..."):
        time.sleep(0.5)
        ingresos_a1, ingresos_a2, vme_a = calcular_vme_opcion_a(
            unidades_a1, precio_a1, prob_a1, unidades_a2, precio_a2, prob_a2
        )
        ingresos_b1, ingresos_b2, vme_b = calcular_vme_opcion_b(
            unidades_b1, precio_b1, prob_b1, unidades_b2, precio_b2, prob_b2, costo_estudio
        )
    
    # Mostrar resultados
    tab1, tab2, tab3 = st.tabs(["📋 Resultados", "📊 Comparación", "💾 Exportar"])
    
    with tab1:
        mostrar_resultados("Opción (b)", ingresos_a1, prob_a1, ingresos_a2, prob_a2, vme_a)
        st.divider()
        mostrar_resultados("Opción (c)", ingresos_b1, prob_b1, ingresos_b2, prob_b2, vme_b, costo_estudio)
    
    with tab2:
        st.header("📈 Comparación Visual")
        comparison_data = pd.DataFrame({
            "Opción": ["(b)", "(c)"],
            "VME": [vme_a, vme_b]
        })
        st.bar_chart(comparison_data.set_index("Opción"), use_container_width=True)
    
    with tab3:
        st.header("💾 Exportar Resultados")
        export_data = pd.DataFrame({
            "Opción": ["(b)", "(b)", "(c)", "(c)"],
            "Escenario": [1, 2, 1, 2],
            "Probabilidad": [prob_a1, prob_a2, prob_b1, prob_b2],
            "Unidades": [unidades_a1, unidades_a2, unidades_b1, unidades_b2],
            "Precio Unitario": [precio_a1, precio_a2, precio_b1, precio_b2],
            "Ingresos": [ingresos_a1, ingresos_a2, ingresos_b1, ingresos_b2],
            "Costo Estudio": [0, 0, costo_estudio, costo_estudio],
            "VME": [vme_a, vme_a, vme_b, vme_b]
        })
        
        st.dataframe(export_data, use_container_width=True)
        
        # Exportación sin xlsxwriter
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            export_data.to_excel(writer, index=False)
        
        st.download_button(
            label="📊 Descargar Excel",
            data=buffer.getvalue(),
            file_name=f"vme_resultados_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.download_button(
            label="📝 Descargar CSV",
            data=export_data.to_csv(index=False).encode('utf-8'),
            file_name=f"vme_resultados_{datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv'
        )
    
    # Recomendación final
    st.divider()
    if vme_b > vme_a:
        st.success(f"## 🏆 Recomendación: Elegir **OPCIÓN (c)** (VME: ${vme_b:,.2f})")
    else:
        st.success(f"## 🏆 Recomendación: Elegir **OPCIÓN (b)** (VME: ${vme_a:,.2f})")

if __name__ == "__main__":
    main()