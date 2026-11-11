package ch.phonedc.pynode

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.net.wifi.WifiManager
import android.os.Build
import android.os.IBinder
import android.os.PowerManager
import androidx.core.app.NotificationCompat
import androidx.core.content.ContextCompat
import java.util.concurrent.Executors

/**
 * Service au premier plan qui garde le serveur Python en vie écran éteint
 * (wake lock + wifi lock) et le relance au démarrage du téléphone (BootReceiver).
 */
class ServerService : Service() {

    companion object {
        const val ACTION_START = "ch.phonedc.pynode.START"
        const val ACTION_STOP = "ch.phonedc.pynode.STOP"
        const val ACTION_RESTART = "ch.phonedc.pynode.RESTART"
        val ACTIONS = setOf(ACTION_START, ACTION_STOP, ACTION_RESTART)

        private const val CHANNEL = "pynode"
        private const val NOTIF_ID = 1
        const val PREFS = "pynode"

        fun send(ctx: Context, action: String) {
            ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit()
                .putBoolean("autostart", action != ACTION_STOP).apply()
            ContextCompat.startForegroundService(ctx, Intent(ctx, ServerService::class.java).setAction(action))
        }
    }

    // Un seul thread : les démarrages/arrêts Python ne se chevauchent pas et ne bloquent pas l'UI.
    private val worker = Executors.newSingleThreadExecutor()
    private var wakeLock: PowerManager.WakeLock? = null
    private var wifiLock: WifiManager.WifiLock? = null

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        goForeground() // obligatoire après startForegroundService, même pour STOP
        when (intent?.action) {
            ACTION_STOP -> worker.execute { Node.stop(this); stopSelf() }
            ACTION_RESTART -> { acquireLocks(); worker.execute { Node.start(this) } } // start() arrête d'abord
            else -> { acquireLocks(); worker.execute { if (!Node.isRunning(this)) Node.start(this) } }
        }
        return START_STICKY // relancé par Android s'il est tué (intent null → START)
    }

    override fun onDestroy() {
        worker.execute { Node.stop(this) }
        worker.shutdown()
        wakeLock?.release()
        wifiLock?.release()
        super.onDestroy()
    }

    private fun goForeground() {
        val nm = getSystemService(NotificationManager::class.java)
        if (Build.VERSION.SDK_INT >= 26) {
            nm.createNotificationChannel(NotificationChannel(CHANNEL, "Serveur", NotificationManager.IMPORTANCE_LOW))
        }
        val open = PendingIntent.getActivity(
            this, 0, Intent(this, MainActivity::class.java), PendingIntent.FLAG_IMMUTABLE
        )
        val notif = NotificationCompat.Builder(this, CHANNEL)
            .setSmallIcon(android.R.drawable.stat_notify_sync)
            .setContentTitle("PyNode actif")
            .setContentText(Node.appDir(this).absolutePath)
            .setContentIntent(open)
            .setOngoing(true)
            .build()
        startForeground(NOTIF_ID, notif)
    }

    @Suppress("DEPRECATION", "WakelockTimeout")
    private fun acquireLocks() {
        if (wakeLock == null) {
            wakeLock = (getSystemService(POWER_SERVICE) as PowerManager)
                .newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "pynode:server")
                .apply { setReferenceCounted(false); acquire() }
        }
        if (wifiLock == null) {
            wifiLock = (applicationContext.getSystemService(WIFI_SERVICE) as WifiManager)
                .createWifiLock(WifiManager.WIFI_MODE_FULL_HIGH_PERF, "pynode:wifi")
                .apply { setReferenceCounted(false); acquire() }
        }
    }
}
