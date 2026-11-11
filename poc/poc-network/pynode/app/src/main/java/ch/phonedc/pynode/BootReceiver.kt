package ch.phonedc.pynode

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent

/** Relance le serveur au démarrage du téléphone s'il tournait avant (dernier ordre ≠ STOP). */
class BootReceiver : BroadcastReceiver() {
    override fun onReceive(ctx: Context, intent: Intent) {
        if (intent.action != Intent.ACTION_BOOT_COMPLETED) return
        if (ctx.getSharedPreferences(ServerService.PREFS, Context.MODE_PRIVATE).getBoolean("autostart", false)) {
            ServerService.send(ctx, ServerService.ACTION_START)
        }
    }
}
