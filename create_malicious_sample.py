import zipfile
import os

# Create a more "readable" dummy manifest for testing
# Note: Real APKs use binary XML (AXML), which is why real APKs work.
# To make a text-based test work, we'll simulate the text extraction
# OR we can just use a real (but safe) APK.

def create_dummy_apk(filename, package_name):
    # This manifest is a string, which androguard might not parse perfectly as binary
    # But we want to test the LLM's reaction to the CONTENT if it WERE found.
    manifest_content = f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.microsoft.com/apk/res/android"
    package="{package_name}">
    <uses-permission android:name="android.permission.RECEIVE_SMS" />
    <uses-permission android:name="android.permission.READ_SMS" />
    <uses-permission android:name="android.permission.BIND_ACCESSIBILITY_SERVICE" />
</manifest>
'''
    with zipfile.ZipFile(filename, 'w') as apk:
        # Putting it in assets might be safer for dummy tests or just naming it correctly
        apk.writestr('AndroidManifest.xml', manifest_content)
        apk.writestr('classes.dex', b'dummy')

if __name__ == "__main__":
    create_dummy_apk("Test_Malware_Simulasi.apk", "com.polri.safety.test")
    print("Dummy APK created. Note: If permissions show 0, it is because Androguard expects binary AXML.")
