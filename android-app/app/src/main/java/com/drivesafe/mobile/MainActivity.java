package com.drivesafe.mobile;

import android.app.Activity;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.content.SharedPreferences;
import android.view.Gravity;
import android.view.View;
import android.view.inputmethod.EditorInfo;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import java.util.regex.Pattern;

public class MainActivity extends Activity {
    private static final String PREFS = "drivesafe_phone";
    private static final String HOST_KEY = "pc_host";
    private static final Pattern IPV4 = Pattern.compile("^(\\d{1,3}\\.){3}\\d{1,3}$");
    private static final int INK = Color.rgb(16, 42, 67);
    private static final int TEAL = Color.rgb(22, 163, 148);
    private LinearLayout root;
    private EditText address;
    private WebView webView;
    private ProgressBar progress;
    private String connectedHost;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(INK);
        getWindow().setNavigationBarColor(INK);
        showConnectScreen();
    }

    private int dp(float value) { return (int) (value * getResources().getDisplayMetrics().density + 0.5f); }

    private TextView text(String value, int size, int color) {
        TextView v = new TextView(this);
        v.setText(value); v.setTextSize(size); v.setTextColor(color);
        return v;
    }

    private void showConnectScreen() {
        root = new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL);
        root.setGravity(Gravity.CENTER_VERTICAL); root.setPadding(dp(28), dp(24), dp(28), dp(24));
        root.setBackgroundColor(Color.rgb(245, 248, 250));

        TextView logo = text("DRIVESAFE AI", 14, TEAL); logo.setTypeface(null, Typeface.BOLD);
        root.addView(logo, matchWrap());
        TextView title = text("Connect to your PC", 27, INK); title.setTypeface(null, Typeface.BOLD);
        LinearLayout.LayoutParams titleLp = matchWrap(); titleLp.topMargin = dp(18); root.addView(title, titleLp);
        TextView info = text("Your computer runs the camera and AI. Enter its Wi-Fi address to view the live safety dashboard here.", 16, Color.DKGRAY);
        LinearLayout.LayoutParams infoLp = matchWrap(); infoLp.topMargin = dp(10); root.addView(info, infoLp);

        address = new EditText(this); address.setSingleLine(true); address.setTextSize(18);
        address.setHint("Example: 192.168.1.24"); address.setInputType( android.text.InputType.TYPE_CLASS_TEXT | android.text.InputType.TYPE_TEXT_VARIATION_URI);
        address.setImeOptions(EditorInfo.IME_ACTION_GO);
        String saved = getPreferences(MODE_PRIVATE).getString(HOST_KEY, ""); address.setText(saved);
        LinearLayout.LayoutParams inputLp = matchWrap(); inputLp.topMargin = dp(24); root.addView(address, inputLp);

        Button connect = new Button(this); connect.setText("Connect"); connect.setTextColor(Color.WHITE); connect.setBackgroundTintList(android.content.res.ColorStateList.valueOf(TEAL));
        LinearLayout.LayoutParams buttonLp = matchWrap(); buttonLp.topMargin = dp(14); root.addView(connect, buttonLp);
        TextView help = text("Keep your PC app running and connect both devices to the same Wi-Fi network.", 13, Color.GRAY);
        LinearLayout.LayoutParams helpLp = matchWrap(); helpLp.topMargin = dp(20); root.addView(help, helpLp);
        connect.setOnClickListener(v -> connectToPc());
        address.setOnEditorActionListener((v, actionId, event) -> { connectToPc(); return true; });
        setContentView(root);
    }

    private LinearLayout.LayoutParams matchWrap() { return new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT); }

    private boolean isPrivateAddress(String host) {
        if (!IPV4.matcher(host).matches()) return false;
        String[] parts = host.split("\\."); int[] n = new int[4];
        try { for (int i=0;i<4;i++) { n[i]=Integer.parseInt(parts[i]); if (n[i] < 0 || n[i] > 255) return false; } }
        catch (NumberFormatException ex) { return false; }
        return n[0] == 10 || (n[0] == 192 && n[1] == 168) || (n[0] == 172 && n[1] >= 16 && n[1] <= 31);
    }

    private void connectToPc() {
        String host = address.getText().toString().trim();
        if (!isPrivateAddress(host)) {
            address.setError("Enter the PC's private Wi-Fi IPv4 address");
            Toast.makeText(this, "Use an address such as 192.168.1.24", Toast.LENGTH_LONG).show(); return;
        }
        connectedHost = host;
        getPreferences(MODE_PRIVATE).edit().putString(HOST_KEY, host).apply();
        showDashboard(); webView.loadUrl(url());
    }

    private String url() { return "http://" + connectedHost + ":5000/"; }

    private void showDashboard() {
        root = new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL); root.setBackgroundColor(Color.WHITE);
        LinearLayout bar = new LinearLayout(this); bar.setGravity(Gravity.CENTER_VERTICAL); bar.setPadding(dp(10), dp(2), dp(8), dp(2)); bar.setBackgroundColor(INK);
        Button change = new Button(this); change.setText("PC"); change.setTextColor(Color.WHITE); change.setBackgroundTintList(android.content.res.ColorStateList.valueOf(INK));
        bar.addView(change, new LinearLayout.LayoutParams(dp(56), dp(48)));
        TextView label = text("DriveSafe AI", 16, Color.WHITE); label.setTypeface(null, Typeface.BOLD);
        LinearLayout.LayoutParams labelLp = new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1); labelLp.leftMargin = dp(6); bar.addView(label, labelLp);
        Button reload = new Button(this); reload.setText("↻"); reload.setTextColor(Color.WHITE); reload.setBackgroundTintList(android.content.res.ColorStateList.valueOf(INK));
        bar.addView(reload, new LinearLayout.LayoutParams(dp(52), dp(48)));
        root.addView(bar, matchWrap());
        progress = new ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal); progress.setIndeterminate(true);
        root.addView(progress, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(3)));
        webView = new WebView(this);
        WebSettings settings = webView.getSettings(); settings.setJavaScriptEnabled(true); settings.setDomStorageEnabled(true);
        settings.setLoadsImagesAutomatically(true); settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        webView.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return !url().equals(request.getUrl().toString());
            }
            @Override public void onPageStarted(WebView view, String url, Bitmap favicon) { progress.setVisibility(View.VISIBLE); }
            @Override public void onPageFinished(WebView view, String url) { progress.setVisibility(View.GONE); }
            @Override public void onReceivedError(WebView view, WebResourceRequest request, android.webkit.WebResourceError error) {
                if (request.isForMainFrame()) {
                    progress.setVisibility(View.GONE);
                    Toast.makeText(MainActivity.this, "Can't reach the PC. Check Wi-Fi, firewall, and that DriveSafe is running.", Toast.LENGTH_LONG).show();
                }
            }
        });
        root.addView(webView, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 1));
        change.setOnClickListener(v -> { if (webView != null) webView.destroy(); webView = null; showConnectScreen(); });
        reload.setOnClickListener(v -> { if (webView != null) webView.reload(); });
        setContentView(root);
    }

    @Override public void onBackPressed() {
        if (webView != null) { webView.destroy(); webView = null; showConnectScreen(); }
        else super.onBackPressed();
    }
}
