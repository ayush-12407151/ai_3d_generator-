import streamlit as st
import subprocess
import os
import ast
import base64

st.set_page_config(page_title="Patent-Grade AI Design System", layout="wide")

st.title("AI-Driven Manufacturable 3D Design System")
st.caption("Auto-correction • Load-aware adaptation • Manufacturability decision")

prompt = st.text_area(
    "Describe what you want to create:",
    placeholder="e.g. Hook to hang headphones, strong"
)

# ---------- STL VIEWER ----------
def stl_viewer_html(path, height=520):
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()

    return f"""
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128/examples/js/loaders/STLLoader.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128/examples/js/controls/OrbitControls.js"></script>
    <div id="viewer"></div>
    <script>
      const scene=new THREE.Scene();
      scene.background=new THREE.Color(0x1e1e1e);
      const camera=new THREE.PerspectiveCamera(70,window.innerWidth/{height},0.1,1000);
      camera.position.set(0,-160,120);
      const renderer=new THREE.WebGLRenderer({{antialias:true}});
      renderer.setSize(window.innerWidth,{height});
      document.getElementById("viewer").appendChild(renderer.domElement);
      new THREE.OrbitControls(camera,renderer.domElement);
      scene.add(new THREE.AmbientLight(0xaaaaaa,0.8));
      const d=new THREE.DirectionalLight(0xffffff,1.2);
      d.position.set(1,1,1);
      scene.add(d);
      const loader=new THREE.STLLoader();
      const bin=atob("{data}");
      const arr=new Uint8Array(bin.length);
      for(let i=0;i<bin.length;i++)arr[i]=bin.charCodeAt(i);
      const geo=loader.parse(arr.buffer); geo.center();
      const mesh=new THREE.Mesh(geo,new THREE.MeshStandardMaterial({{color:0x4caf50}}));
      scene.add(mesh);
      function anim(){{requestAnimationFrame(anim);mesh.rotation.z+=0.003;renderer.render(scene,camera);}}
      anim();
    </script>
    """

# ---------- ACTION ----------
if st.button("Generate Design"):
    for f in ["output/model.stl", "output/decision.txt"]:
        if os.path.exists(f):
            os.remove(f)

    subprocess.run(["python", "generator.py", prompt])

    if not os.path.exists("output/decision.txt"):
        st.error("Generation failed.")
    else:
        decision = {}
        with open("output/decision.txt") as f:
            for line in f:
                k, v = line.strip().split("=", 1)
                decision[k] = v

        params = ast.literal_eval(decision["PARAMS"])
        left, right = st.columns([1.2, 1.8])

        # ---------- LEFT ----------
        with left:
            st.subheader("AI Design Reasoning (Patent-Critical)")

            st.markdown("### 1️⃣ Geometry Family")
            st.code(decision["FAMILY"].capitalize())

            st.markdown("### 2️⃣ Inferred & Adapted Parameters")
            for k, v in params.items():
                st.write(f"- **{k}** : {v}")

            st.markdown("### 3️⃣ Manufacturability Decision")
            if decision["APPROVED"] == "True":
                st.success("APPROVED – self-supporting")
            else:
                st.error("REJECTED")

            for r in decision["REASONS"].split(";"):
                st.write(f"- {r}")

            st.markdown("### 4️⃣ Strength & Stability Score")
            st.metric(
                "Structural Score",
                f"{decision['STRENGTH_SCORE']} / 100",
                decision["STRENGTH_LABEL"]
            )

            if decision["CORRECTIONS"]:
                st.markdown("### Automatic Design Corrections")
                for c in decision["CORRECTIONS"].split(";"):
                    st.write(f"- {c}")

        # ---------- RIGHT ----------
        with right:
            st.subheader("3D Model Preview")
            if decision["APPROVED"] == "True":
                st.components.v1.html(
                    stl_viewer_html("output/model.stl"),
                    height=550
                )
                with open("output/model.stl", "rb") as f:
                    st.download_button("Download STL", f, "model.stl")
            else:
                st.warning("Model not generated due to rejection.")
