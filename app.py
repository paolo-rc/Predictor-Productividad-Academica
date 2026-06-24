from shiny import App, ui, render, reactive
import joblib
import pandas as pd

# ==========================================
# 1. CARGAR EL MODELO
# ==========================================
modelo = joblib.load('modelo_random_forest.joblib')
columnas_esperadas = modelo.feature_names_in_

# ==========================================
# 2. INTERFAZ DE USUARIO
# ==========================================
app_ui = ui.page_fluid(
    ui.h2("Monitor de Productividad y Salud Académica"),
    ui.p("Simulador predictivo ajustado por neurociencia y eficiencia operativa."),
    
    ui.layout_sidebar(
        ui.sidebar(
            ui.h4("Parámetros Operativos:"),
            ui.input_slider("study_hours", "Horas de Estudio al Día", min=0.0, max=12.0, value=5.0, step=0.5),
            ui.input_slider("focus_score", "Nivel de Concentración (0-10)", min=0.0, max=10.0, value=7.0, step=0.5),
            ui.input_slider("sleep_hours", "Horas de Sueño", min=0.0, max=14.0, value=8.0, step=0.5),
            ui.input_slider("phone_usage", "Horas de Uso del Celular", min=0.0, max=16.0, value=2.0, step=0.5),
            ui.input_slider("stress_level", "Nivel de Estrés (0-10)", min=0.0, max=10.0, value=4.0, step=0.5),
            ui.input_slider("attendance", "Porcentaje de Asistencia (%)", min=0, max=100, value=90, step=1)
        ),
        
        ui.card(
            ui.h3("Tu Score de Efectividad Real:"),
            ui.output_text_verbatim("resultado_scoring"),
            ui.p(ui.em("* Puntaje calibrado: Recompensa el trabajo inteligente y penaliza la sobrecarga y distractores.")),
            ui.br(),
            ui.h4("Triage Académico y Recomendación:"),
            ui.output_ui("recomendacion") 
        )
    )
)

# ==========================================
# 3. LÓGICA DEL SERVIDOR (Cerebro Balanceado)
# ==========================================
def server(input, output, session):
    
    # El decorador @reactive.calc OBLIGA a Shiny a actualizar en vivo cualquier movimiento
    @reactive.calc
    def calcular_score_real():
        # 1. Llenamos el DataFrame para el algoritmo
        df_input = pd.DataFrame(0.0, index=[0], columns=columnas_esperadas)
        if 'study_hours_per_day' in df_input.columns: df_input.at[0, 'study_hours_per_day'] = input.study_hours()
        if 'sleep_hours' in df_input.columns: df_input.at[0, 'sleep_hours'] = input.sleep_hours()
        if 'phone_usage_hours' in df_input.columns: df_input.at[0, 'phone_usage_hours'] = input.phone_usage()
        if 'stress_level' in df_input.columns: df_input.at[0, 'stress_level'] = input.stress_level()
        if 'attendance_percentage' in df_input.columns: df_input.at[0, 'attendance_percentage'] = input.attendance()
        if 'focus_score' in df_input.columns: df_input.at[0, 'focus_score'] = input.focus_score()

        # 2. Score base del Random Forest
        score_base = modelo.predict(df_input)[0]
        score_ajustado = score_base
        
        # 3. Extraemos las variables para aplicar Criterio de Negocio
        estudio = input.study_hours()
        sueno = input.sleep_hours()
        celular = input.phone_usage()
        enfoque = input.focus_score()
        
        # ---------------------------------------------------------
        # FASE 1: BONIFICACIONES (La recompensa por trabajar bien)
        # ---------------------------------------------------------
        if 4.0 <= estudio <= 6.0: score_ajustado += 18
        if 7.0 <= sueno <= 9.0: score_ajustado += 12
        if celular <= 2.5: score_ajustado += 10
        if enfoque >= 8.0: score_ajustado += 15 # <-- BONO: Alta concentración
            
        # ---------------------------------------------------------
        # FASE 2: PENALIZACIONES (Los límites biológicos)
        # ---------------------------------------------------------
        if estudio > 6.5: score_ajustado -= ((estudio - 6.5) * 12)
        if sueno < 6.0: score_ajustado -= ((6.0 - sueno) * 10)
        if celular > 4.0: score_ajustado -= ((celular - 4.0) * 6)
        if enfoque <= 4.0: score_ajustado -= 12 # <-- CASTIGO: Falta de concentración
            
        # Limitar estrictamente entre 0 y 100
        return max(0, min(100, score_ajustado))

    @render.text
    def resultado_scoring():
        return f"{round(calcular_score_real(), 1)} / 100"
    
    @render.ui
    def recomendacion():
        score_final = calcular_score_real()
        estudio = input.study_hours()
        sueno = input.sleep_hours()
        celular = input.phone_usage()
        enfoque = input.focus_score()
        
        # Alertas organizadas por prioridad (Criterio Analista)
        if estudio > 6.5:
            return ui.HTML(f"""
                <div style='color: #D32F2F; background-color: #FFEBEE; padding: 15px; border-radius: 5px; border-left: 5px solid #D32F2F;'>
                    <strong>⚠️ Alerta de Burnout (Ley de Rendimientos Decrecientes):</strong><br>
                    El sistema ha penalizado tu puntaje. Estudiar {estudio} horas satura la memoria de trabajo. Reduce a bloques de 5 horas para activar las bonificaciones.
                </div>
            """)
        elif sueno < 6.0:
            return ui.HTML(f"""
                <div style='color: #E65100; background-color: #FFF3E0; padding: 15px; border-radius: 5px; border-left: 5px solid #E65100;'>
                    <strong>⚠️ Alerta de Consolidación de Memoria:</strong><br>
                    Dormir solo {sueno} horas frena el traspaso de información. El sistema te está restando puntos de eficiencia porque tu cerebro no se está recuperando.
                </div>
            """)
        elif enfoque <= 4.0: # <-- NUEVA ALERTA DE INTERFAZ
            return ui.HTML(f"""
                <div style='color: #8E24AA; background-color: #F3E5F5; padding: 15px; border-radius: 5px; border-left: 5px solid #8E24AA;'>
                    <strong>⚠️ Alerta de Calidad de Estudio:</strong><br>
                    Estás invirtiendo tiempo, pero tu nivel de concentración ({enfoque}/10) es muy bajo. Recuerda que la calidad del enfoque es el segundo factor predictivo más importante.
                </div>
            """)
        elif celular > 4.0:
            return ui.HTML(f"""
                <div style='color: #F57C00; background-color: #FFF8E1; padding: 15px; border-radius: 5px; border-left: 5px solid #F57C00;'>
                    <strong>⚠️ Fuga de Atención:</strong><br>
                    Tu tiempo en pantalla ({celular} hrs) diluye el impacto de tus horas de estudio. Bajar este número a menos de 2.5 horas disparará un multiplicador positivo.
                </div>
            """)
        elif score_final >= 85:
            return ui.HTML("""
                <div style='color: #2E7D32; background-color: #E8F5E9; padding: 15px; border-radius: 5px; border-left: 5px solid #2E7D32;'>
                    <strong>🎯 ¡Zona de Máxima Eficiencia!</strong><br>
                    El sistema ha detectado que estás trabajando de forma inteligente. Has activado las bonificaciones por enfoque y descanso.
                </div>
            """)
        else:
            return ui.HTML("""
                <div style='color: #1565C0; background-color: #E3F2FD; padding: 15px; border-radius: 5px; border-left: 5px solid #1565C0;'>
                    <strong>ℹ️ Oportunidad de Mejora:</strong><br>
                    Vas por buen camino. Intenta acercar tus horas de estudio al rango óptimo y asegurar un entorno libre de distracciones.
                </div>
            """)

# ==========================================
# 4. ENSAMBLAR
# ==========================================
app = App(app_ui, server)