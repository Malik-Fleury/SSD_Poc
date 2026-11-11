package ch.phonedc.pynode

import android.Manifest
import android.annotation.SuppressLint
import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.provider.Settings
import android.widget.Button
import android.widget.TextView
import java.util.concurrent.Executors

/** Écran de contrôle : démarrer/arrêter/recharger, adresses, journal en direct. */
class MainActivity : Activity() {
    private lateinit var status: TextView
    private lateinit var logView: TextView
    private val handler = Handler(Looper.getMainLooper())
    private val io = Executors.newSingleThreadExecutor()
    private val poll = object : Runnable {
        override fun run() {
            refresh()
            handler.postDelayed(this, 1000)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        status = findViewById(R.id.status)
        logView = findViewById(R.id.log)

        findViewById<Button>(R.id.start).setOnClickListener { ServerService.send(this, ServerService.ACTION_START) }
        findViewById<Button>(R.id.stop).setOnClickListener { ServerService.send(this, ServerService.ACTION_STOP) }
        findViewById<Button>(R.id.restart).setOnClickListener { ServerService.send(this, ServerService.ACTION_RESTART) }
        findViewById<Button>(R.id.battery).setOnClickListener { askIgnoreBatteryOptimizations() }

        if (Build.VERSION.SDK_INT >= 33) requestPermissions(arrayOf(Manifest.permission.POST_NOTIFICATIONS), 0)
        handleIntent(intent)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        handleIntent(intent)
    }

    /** Ordres envoyés depuis le PC : adb shell am start -n ch.phonedc.pynode/.MainActivity -a <ACTION> */
    private fun handleIntent(intent: Intent?) {
        val action = intent?.action ?: return
        if (action in ServerService.ACTIONS) ServerService.send(this, action)
    }

    override fun onResume() {
        super.onResume()
        handler.post(poll)
    }

    override fun onPause() {
        handler.removeCallbacks(poll)
        super.onPause()
    }

    private fun refresh() {
        io.execute {
            val text = try {
                Node.statusText(this) + "\nIP : " + Node.ipAddresses().joinToString(" | ")
            } catch (e: Exception) {
                "Python indisponible : $e"
            }
            val logs = try { Node.logs(this) } catch (e: Exception) { "" }
            handler.post {
                status.text = text
                logView.text = logs
            }
        }
    }

    @SuppressLint("BatteryLife")
    private fun askIgnoreBatteryOptimizations() {
        startActivity(Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS, Uri.parse("package:$packageName")))
    }
}
