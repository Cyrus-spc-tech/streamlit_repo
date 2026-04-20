import streamlit as st 
from cl import EXAA
from exa_py import Exa

st.set_page_config(page_title="Search Eng")

# Initialize the EXAA class
@st.cache_resource
def get_exa_client():
    return EXAA()

def main():
    st.title("🔍 Search Engine")
    st.markdown("---")
    
    # Search input
    search_query = st.text_input("Enter your search query:", placeholder="Search the web...")
    
    if st.button("Search") or search_query:
        if search_query:
            with st.spinner("Searching..."):
                try:
                    exa_client = get_exa_client()
                    results = exa_client.exa.search_and_contents(
                        f"{search_query}",
                        text=True,
                        num_results=10
                    )
                    
                    if results.results:
                        st.success(f"Found {len(results.results)} results")
                        
                        for i, result in enumerate(results.results, 1):
                            with st.expander(f"{result.title}", expanded=i==1):
                                st.markdown(f"**URL:** {result.url}")
                                if result.summary:
                                    st.markdown(f"**Summary:** {result.summary}")
                                if hasattr(result, 'text') and result.text:
                                    with st.expander("View Content"):
                                        st.text_area("", result.text, height=200, disabled=True)
                                st.markdown("---")
                    else:
                        st.warning("No results found. Try a different search query.")
                        
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please enter a search query.")
    
    st.markdown("---")
    st.markdown("*Powered by Exa API*")
        
        

if __name__ == "__main__":
    main()
