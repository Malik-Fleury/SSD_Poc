package ch.phonedc.pynode

import android.content.Context
import android.util.Log
import com.chaquo.python.PyObject
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import java.io.File
import java.net.Inet4Address
import java.net.NetworkInterface

/** Pont vers le lanceur Python (src/main/python/pynode/launcher.py). */
object Node {
    private const val TAG = "PyNode"

    /** Dossier de l'appli utilisateur : /sdcard/Android/data/ch.phonedc.pynode/files (adb push, MTP). */
    fun appDir(ctx: Context): File = ctx.getExternalFilesDir(null) ?: ctx.filesDir

    @Synchronized
    private fun launcher(ctx: Context): PyObject {
        if (!Python.isStarted()) Python.start(AndroidPlatform(ctx.applicationContext))
        return Python.getInstance().getModule("pynode.launcher")
    }

    fun start(ctx: Context) {
        try {
            launcher(ctx).callAttr("start", appDir(ctx).absolutePath, ctx.applicationContext)
        } catch (e: Exception) {
            Log.e(TAG, "Échec du démarrage", e)
        }
    }

    fun stop(ctx: Context) {
        try {
            launcher(ctx).callAttr("stop")
        } catch (e: Exception) {
            Log.e(TAG, "Échec de l'arrêt", e)
        }
    }

    fun isRunning(ctx: Context): Boolean = launcher(ctx).callAttr("is_running").toBoolean()

    fun statusText(ctx: Context): String = launcher(ctx).callAttr("status_text").toString()

    fun logs(ctx: Context): String = launcher(ctx).callAttr("logs").toString()

    /** Adresses IPv4 du téléphone (Wi-Fi, modem USB...), pour savoir où le joindre. */
    fun ipAddresses(): List<String> = try {
        NetworkInterface.getNetworkInterfaces().toList()
            .filter { it.isUp && !it.isLoopback }
            .flatMap { ni ->
                ni.inetAddresses.toList().filterIsInstance<Inet4Address>()
                    .map { "${ni.name} ${it.hostAddress}" }
            }
    } catch (e: Exception) {
        emptyList()
    }
}
