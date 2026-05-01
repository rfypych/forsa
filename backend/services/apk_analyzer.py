from androguard.core.apk import APK
import io
import zipfile
import re

def extract_apk_info(apk_bytes: bytes):
    """
    Extracts package name and permissions from APK bytes.
    Includes a fallback parser for text-based manifests (dummy tests).
    """
    try:
        # Step 1: Try standard Androguard (for binary AXML)
        a = APK(apk_bytes, raw=True)
        package_name = a.get_package()
        permissions = a.get_permissions()
        
        # Step 2: Fallback if 0 permissions found (might be a text-based dummy manifest)
        if not permissions:
            with zipfile.ZipFile(io.BytesIO(apk_bytes)) as z:
                if 'AndroidManifest.xml' in z.namelist():
                    manifest_data = z.read('AndroidManifest.xml').decode('utf-8', errors='ignore')
                    
                    # Extract permissions using regex
                    perm_pattern = r'android:name=["\'](android\.permission\.[A-Z_]+)["\']'
                    permissions = list(set(re.findall(perm_pattern, manifest_data)))
                    
                    # Extract package name
                    pkg_pattern = r'package=["\']([^"\']+)["\']'
                    pkg_match = re.search(pkg_pattern, manifest_data)
                    if pkg_match:
                        package_name = pkg_match.group(1)

        permission_str = "\n".join(permissions) if permissions else "None detected"
        
        summary = (
            f"Package Name: {package_name or 'Unknown'}\n"
            f"Permissions Found ({len(permissions)}):\n"
            f"{permission_str}"
        )
        
        return {
            "success": True,
            "package_name": package_name,
            "permissions": permissions,
            "summary": summary
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
