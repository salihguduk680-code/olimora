package com.olimora.app

import android.content.Context
import com.google.firebase.FirebaseApp
import com.google.firebase.messaging.FirebaseMessaging
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import com.olimora.app.data.registerPushInstallation
import com.olimora.app.data.SessionStore
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException
import kotlin.coroutines.suspendCoroutine

internal suspend fun registerFirebaseInstallation(context: Context, authToken: String): Boolean {
    FirebaseApp.initializeApp(context) ?: return false
    val registrationToken = suspendCoroutine { continuation ->
        FirebaseMessaging.getInstance().token.addOnCompleteListener { task ->
            if (task.isSuccessful) {
                continuation.resume(task.result)
            } else {
                continuation.resumeWithException(
                    task.exception ?: IllegalStateException("Bildirim anahtarı alınamadı."),
                )
            }
        }
    }
    registerPushInstallation(authToken, registrationToken)
    return true
}

class OlimoraMessagingService : FirebaseMessagingService() {
    override fun onNewToken(token: String) {
        val authToken = SessionStore(applicationContext).token() ?: return
        CoroutineScope(SupervisorJob() + Dispatchers.IO).launch {
            runCatching { registerPushInstallation(authToken, token) }
        }
    }

    override fun onMessageReceived(message: RemoteMessage) {
        val senderName = message.data["sender_name"]
        val preview = message.data["message_preview"]
        val title = message.notification?.title
            ?: senderName?.let { "$it sana yazdı" }
            ?: "Olimora'da yeni mesajın var"
        val body = message.notification?.body
            ?: preview
            ?: "Bir arkadaşın sana yazdı."
        applicationContext.showMessageNotification(unreadCount = 1, title = title, body = body)
    }
}
