import streamlit as st
import streamlit.components.v1 as components
from src.config import STYLE_CSS_PATH, ANIMATION_CSS_PATH

def inject_styles_and_scripts():
    try:
        with open(STYLE_CSS_PATH, 'r') as f:
            custom_css = f.read()
        with open(ANIMATION_CSS_PATH, 'r') as f:
            anim_css = f.read()
            
        st.markdown('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Russo+One&family=Syncopate:wght@700&display=swap" rel="stylesheet">', unsafe_allow_html=True)
        st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)
        st.markdown(f"<style>{anim_css}</style>", unsafe_allow_html=True)
        st.markdown("<div class='main-container-bg'></div>", unsafe_allow_html=True)
        
        components.html("""
        <script>
        (function() {
            const parentDoc = window.parent.document;
            if (parentDoc._chaseBikeReady) return;
            parentDoc._chaseBikeReady = true;
            
            const stApp = parentDoc.querySelector('.stApp');
            if (!stApp) return;
            
            const bike = parentDoc.createElement('div');
            bike.textContent = '🏍️';
            bike.style.cssText = 'position:fixed;font-size:28px;pointer-events:none;z-index:999999;transform-origin:center center;left:-100px;top:-100px;transition:none;';
            stApp.appendChild(bike);
            
            let mouseX = 0, mouseY = 0;
            let bikeX = -100, bikeY = -100;
            let lastTrackX = -100, lastTrackY = -100;
            let orbiting = false;
            let orbitRect = null;
            let orbitProgress = 0;
            
            parentDoc.addEventListener('mousemove', function(e) {
                mouseX = e.clientX;
                mouseY = e.clientY;
                
                const target = e.target;
                if (!target) return;
                
                const interactive = target.closest(
                    '[data-testid="stPlotlyChart"], .js-plotly-plot, .plotly, ' +
                    'div.business-card, div.kpi-card, [data-testid="stDataFrame"], [data-testid="stTable"], ' +
                    'table, button, a, select, input, textarea, ' +
                    '[role="button"], [role="tab"], [role="option"], ' +
                    '[data-baseweb="select"], [data-testid="stSelectbox"], ' +
                    'iframe'
                );
                
                if (interactive) {
                    if (!orbiting) {
                        orbiting = true;
                        orbitRect = interactive.getBoundingClientRect();
                        orbitProgress = 0;
                    }
                } else {
                    orbiting = false;
                    orbitRect = null;
                }
            });
            
            function loop() {
                let targetX = mouseX;
                let targetY = mouseY;
                
                const configEl = parentDoc.getElementById('bike-config');
                const enabled = configEl ? configEl.getAttribute('data-enabled') === 'true' : true;
                
                if (!enabled) {
                    targetX = 45;
                    targetY = window.innerHeight - 45;
                } else if (orbiting && orbitRect) {
                    const padding = 35;
                    const left = orbitRect.left - padding;
                    const top = orbitRect.top - padding;
                    const right = orbitRect.right + padding;
                    const bottom = orbitRect.bottom + padding;
                    
                    const W = right - left;
                    const H = bottom - top;
                    const perimeter = 2 * (W + H);
                    
                    orbitProgress = (orbitProgress + 3) % perimeter; 
                    
                    if (orbitProgress < W) {
                        targetX = left + orbitProgress;
                        targetY = top;
                    } else if (orbitProgress < W + H) {
                        targetX = right;
                        targetY = top + (orbitProgress - W);
                    } else if (orbitProgress < 2 * W + H) {
                        targetX = right - (orbitProgress - (W + H));
                        targetY = bottom;
                    } else {
                        targetX = left;
                        targetY = bottom - (orbitProgress - (2 * W + H));
                    }
                }
                
                bikeX += (targetX - bikeX) * 0.04;
                bikeY += (targetY - bikeY) * 0.04;
                
                const dx = targetX - bikeX;
                const dy = targetY - bikeY;
                const speed = Math.hypot(dx, dy);
                let angle = Math.atan2(dy, dx) * (180 / Math.PI);
                
                let scaleX = -1;
                let rotateAngle = angle;
                if (Math.abs(angle) > 90) {
                    scaleX = 1;
                    rotateAngle = angle - 180;
                }
                
                const finalRotation = scaleX === -1 ? -rotateAngle : rotateAngle;
                
                bike.style.left = bikeX + 'px';
                bike.style.top = bikeY + 'px';
                bike.style.transform = `translate(-50%,-50%) scaleX(${scaleX}) rotate(${finalRotation}deg)`;
                
                const dist = Math.hypot(bikeX - lastTrackX, bikeY - lastTrackY);
                if (dist > 14 && speed > 1.2) {
                    const angleRad = finalRotation * (Math.PI / 180);
                    const trackX = bikeX + scaleX * (-11 * Math.sin(angleRad));
                    const trackY = bikeY + 11 * Math.cos(angleRad);
                    
                    const t = parentDoc.createElement('div');
                    t.className = 'bike-tire-track';
                    t.style.left = trackX + 'px';
                    t.style.top = trackY + 'px';
                    t.style.transform = 'translate(-50%,-50%) rotate(' + angle + 'deg)';
                    stApp.appendChild(t);
                    lastTrackX = bikeX;
                    lastTrackY = bikeY;
                    setTimeout(function() { t.remove(); }, 1000);
                }
                
                requestAnimationFrame(loop);
            }
            
            requestAnimationFrame(loop);
        })();
        </script>
        """, height=0)
    except FileNotFoundError:
        st.warning("Stylesheets not found in assets/ directory.")

def render_sidebar_logo():
    st.sidebar.markdown("""
    <div class="sidebar-header-box">
        <h2 class="sidebar-title">VEXAR DRIVE</h2>
        <span class="sidebar-subtitle">Control Center Portal</span>
    </div>
    """, unsafe_allow_html=True)
    
    page = st.sidebar.radio(
        "Perspective Navigation",
        ["Driver Behaviour Dashboard", "Vehicle Health Dashboard"]
    )
    
    st.sidebar.markdown("<br><br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    bike_enabled = st.sidebar.checkbox("Enable Chase Bike", value=True)
    st.markdown(f"<div id='bike-config' data-enabled='{'true' if bike_enabled else 'false'}'></div>", unsafe_allow_html=True)
    
    return page

layout_theme = dict(
    template='plotly_white',
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#111111', family='Russo One, sans-serif'),
    legend=dict(font=dict(color='#111111')),
    hoverlabel=dict(
        bgcolor='#ffffff',
        bordercolor='#e5e7eb',
        font=dict(color='#111111', family='Russo One, sans-serif', size=13)
    ),
    xaxis=dict(
        showline=True,
        linecolor='#cbd5e1',
        linewidth=1,
        gridcolor='#f3f4f6',
        zerolinecolor='#cbd5e1',
        tickfont=dict(color='#4b5563'),
        title_font=dict(color='#111111'),
        fixedrange=True
    ),
    yaxis=dict(
        showline=True,
        linecolor='#cbd5e1',
        linewidth=1,
        gridcolor='#f3f4f6',
        zerolinecolor='#cbd5e1',
        tickfont=dict(color='#4b5563'),
        title_font=dict(color='#111111'),
        fixedrange=True
    )
)
