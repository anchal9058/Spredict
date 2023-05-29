import streamlit as st
import requests


DEFAULT_SEQ = "MGSSHHHHHHSSGLVPRGSHMRGPNPTAASLEASAGPFTVRSFTVSRPSGYGAGTVYYPTNAGGTVGAIAIVPGYTARQSSIKWWGPRLASHGFVVITIDTNSTLDQPSSRSSQQMAALRQVASLNGTSSSPIYGKVDTARMGVMGWSMGGGGSLISAANNPSLKAAAPQAPWDSSTNFSSVTVPTLIFACENDSIAPVNSSALPIYDSMSRNAKQFLEINGGSHSCANSGNSNQALIGKKGVAWMKRFMDNDTRYSTFACENPNSTRVSDFRTANCSLEDPAANKARKEAELAAATAEQ"


from Bio.PDB.PDBList import PDBList
from Bio.PDB import PDBParser

def read_mol(pdb_string):
    pdb_file = "temp.pdb"

    # Save the PDB string to a temporary file
    with open(pdb_file, "w") as fp:
        fp.write(pdb_string)

    # Use the PDBParser to parse the temporary file
    parser = PDBParser()
    structure = parser.get_structure("protein", pdb_file)

    # Extract the chain and residue information
    chains = []
    residues = []
    for model in structure:
        for chain in model:
            chains.append(chain.id)
            for residue in chain:
                residues.append(residue.resname.strip())

    # Remove the temporary file
    os.remove(pdb_file)

    # Return the chains and residues
    return chains, residues




def molecule(input_pdb):
    mol = read_mol(input_pdb)

    x = (
        """<!DOCTYPE html>
        <html>
        <head>    
    <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
    <style>
    body{
        font-family:sans-serif
    }
    .mol-container {
    width: 100%;
    height: 380px;
    position: relative;
    }
    .mol-container select{
        background-image:None;
    }
    </style>
    <script src="https://3Dmol.csb.pitt.edu/build/3Dmol-min.js"></script>
    </head>
    <body style="overflow: hidden;">  
    <div id="container" class="mol-container"></div>
  
            <script>
               let pdb = `"""
        + mol
        + """`  
      
             $(document).ready(function () {
                let element = $("#container");
                let config = { backgroundColor: "white" };
                let viewer = $3Dmol.createViewer(element, config);
                let colorAlpha = function (atom) {
                    if (atom.b < 0.5) {
                        return "OrangeRed";
                    } else if (atom.b < 0.7) {
                        return "Gold";
                    } else if (atom.b < 0.9) {
                        return "MediumTurquoise";
                    } else {
                        return "Blue";
                    }
                };
                
                viewer.addModel(pdb, "pdb");
                // set plddt coloring
                viewer.getModel(0).setStyle({cartoon: { colorfunc: colorAlpha }});
                // display pLDDT tooltips when hovering over atoms
                viewer.getModel(0).setHoverable({}, true,
                        function (atom, viewer, event, container) {
                            if (!atom.label) {
                                atom.label = viewer.addLabel(atom.resn + atom.resi + " pLDDT=" + atom.b, { position: atom, backgroundColor: "mintcream", fontColor: "black" });
                            }
                        },
                        function (atom, viewer) {
                            if (atom.label) {
                                viewer.removeLabel(atom.label);
                                delete atom.label;
                            }
                        }
                    );
                viewer.zoomTo();
                viewer.render();
                viewer.zoom(1.2, 2000);
              })
        </script>
        </body></html>"""
    )

    return f"""<iframe style="width: 100%; height: 380px" name="result" allow="midi; geolocation; microphone; camera; 
    display-capture; encrypted-media;" sandbox="allow-modals allow-forms 
    allow-scripts allow-same-origin allow-popups 
    allow-top-navigation-by-user-activation allow-downloads" allowfullscreen="" 
    allowpaymentrequest="" frameborder="0" srcdoc='{x}'></iframe>"""


def update(sequence=DEFAULT_SEQ):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    response = requests.post('https://api.esmatlas.com/foldSequence/v1/pdb/', headers=headers, data=sequence)
    name = sequence[:3] + sequence[-3:]
    pdb_string = response.content.decode('utf-8')

    return molecule(pdb_string)


def suggest(option):
    if option == "Plastic degradation protein":
        suggestion = "MGSSHHHHHHSSGLVPRGSHMRGPNPTAASLEASAGPFTVRSFTVSRPSGYGAGTVYYPTNAGGTVGAIAIVPGYTARQSSIKWWGPRLASHGFVVITIDTNSTLDQPSSRSSQQMAALRQVASLNGTSSSPIYGKVDTARMGVMGWSMGGGGSLISAANNPSLKAAAPQAPWDSSTNFSSVTVPTLIFACENDSIAPVNSSALPIYDSMSRNAKQFLEINGGSHSCANSGNSNQALIGKKGVAWMKRFMDNDTRYSTFACENPNSTRVSDFRTANCSLEDPAANKARKEAELAAATAEQ"
    elif option == "Antifreeze protein":
        suggestion = "QCTGGADCTSCTGACTGCGNCPNAVTCTNSQHCVKANTCTGSTDCNTAQTCTNSKDCFEANTCTDSTNCYKATACTNSSGCPGH"
    elif option == "AI Generated protein":
        suggestion = "MSGMKKLYEYTVTTLDEFLEKLKEFILNTSKDKIYKLTITNPKLIKDIGKAIAKAAEIADVDPKEIEEMIKAVEENELTKLVITIEQTDDKYVIKVELENEDGLVHSFEIYFKNKEEMEKFLELLEKLISKLSGS"
    elif option == "7-bladed propeller fold":
        suggestion = "VKLAGNSSLCPINGWAVYSKDNSIRIGSKGDVFVIREPFISCSHLECRTFFLTQGALLNDKHSNGTVKDRSPHRTLMSCPVGEAPSPYNSRFESVAWSASACHDGTSWLTIGISGPDNGAVAVLKYNGIITDTIKSWRNNILRTQESECACVNGSCFTVMTDGPSNGQASYKIFKMEKGKVVKSVELDAPNYHYEECSCYPNAGEITCVCRDNWHGSNRPWVSFNQNLEYQIGYICSGVFGDNPRPNDGTGSCGPVSSNGAYGVKGFSFKYGNGVWIGRTKSTNSRSGFEMIWDPNGWTETDSSFSVKQDIVAITDWSGYSGSFVQHPELTGLDCIRPCFWVELIRGRPKESTIWTSGSSISFCGVNSDTVGWSWPDGAELPFTIDK"
    else:
        suggestion = ""
    return suggestion


def main():
    st.markdown("""
        <div style="text-align: center; max-width: 700px; margin: 0 auto;">
            <div style="display: inline-flex; align-items: center; gap: 10px;">
                <h1>Protein Folding Prediction</h1>
                <img src="https://www.proteindatabank.org/img/logo/pdb_logo.png" alt="PDB Logo" width="40">
            </div>
            <p style="font-size: 18px;">This web app uses the AlphaFold2-based protein folding prediction API to predict the 3D structure of a given protein sequence.</p>
        </div>
        """, unsafe_allow_html=True)

    st.sidebar.header("Options")
    selected_option = st.sidebar.selectbox("Select a protein type:", ["Plastic degradation protein", "Antifreeze protein", "AI Generated protein", "7-bladed propeller fold"])

    st.sidebar.header("Custom Sequence")
    sequence = st.sidebar.text_area("Enter a protein sequence")

    if sequence:
        result = update(sequence)
        st.write(result)
    else:
        suggested_sequence = suggest(selected_option)
        if suggested_sequence:
            result = update(suggested_sequence)
            st.write(result)
        else:
            st.write("Please enter a custom sequence or select a protein type from the options.")


if __name__ == "__main__":
    main()

