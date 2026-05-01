import httpx
from bs4 import BeautifulSoup

async def extract_url_info(url: str):
    """
    Extracts metadata and basic content from a URL.
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
        
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url)
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        title = soup.title.string if soup.title else "No Title"
        meta_description = ""
        meta_desc_tag = soup.find("meta", attrs={"name": "description"})
        if meta_desc_tag:
            meta_description = meta_desc_tag.get("content", "")
            
        # Get some text from the body to help LLM
        # Limit to first 2000 characters to avoid token bloating
        body_text = soup.body.get_text(separator=" ", strip=True)[:2000] if soup.body else "No Body Content"
        
        summary = (
            f"URL Analyzed: {url}\n"
            f"Page Title: {title}\n"
            f"Meta Description: {meta_description}\n"
            f"Body Snippet: {body_text}"
        )
        
        return {
            "success": True,
            "url": url,
            "title": title,
            "summary": summary
        }
    except Exception as e:
        error_msg = str(e)
        # Jika website mati/offline (biasa terjadi pada web phishing hit-and-run)
        summary = (
            f"URL Analyzed: {url}\n"
            f"Status: Website tidak dapat diakses (Offline/Unreachable)\n"
            f"Error Detail: {error_msg}\n"
            f"Konteks Analisa: Situs phishing atau penipuan seringkali mati atau dihapus dalam beberapa hari setelah beroperasi. Tidak dapatnya situs ini diakses adalah sebuah anomali yang patut diwaspadai jika tautan ini menyebar di masyarakat."
        )
        return {
            "success": True,
            "url": url,
            "title": "Offline / Unreachable",
            "summary": summary
        }
