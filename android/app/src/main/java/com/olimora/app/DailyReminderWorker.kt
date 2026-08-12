package com.olimora.app

import android.Manifest
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.content.ContextCompat
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import java.time.Duration
import java.time.ZonedDateTime
import java.util.concurrent.TimeUnit

private const val DAILY_REMINDER_WORK = "olimora_daily_reminder"

internal fun scheduleDailyOlimoraReminder(context: Context) {
    val now = ZonedDateTime.now()
    var nextReminder = now.withHour(12).withMinute(30).withSecond(0).withNano(0)
    if (!nextReminder.isAfter(now)) nextReminder = nextReminder.plusDays(1)
    val initialDelay = Duration.between(now, nextReminder)
    val request = PeriodicWorkRequestBuilder<DailyReminderWorker>(24, TimeUnit.HOURS)
        .setInitialDelay(initialDelay)
        .build()
    WorkManager.getInstance(context).enqueueUniquePeriodicWork(
        DAILY_REMINDER_WORK,
        ExistingPeriodicWorkPolicy.UPDATE,
        request,
    )
}

internal fun cancelDailyOlimoraReminder(context: Context) {
    WorkManager.getInstance(context).cancelUniqueWork(DAILY_REMINDER_WORK)
}

class DailyReminderWorker(
    appContext: Context,
    params: WorkerParameters,
) : CoroutineWorker(appContext, params) {
    override suspend fun doWork(): Result {
        if (
            Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
            ContextCompat.checkSelfPermission(
                applicationContext,
                Manifest.permission.POST_NOTIFICATIONS,
            ) != PackageManager.PERMISSION_GRANTED
        ) return Result.success()

        val messages = listOf(
            "Çay molasında bugün Olimora'ya baktın mı? ✦",
            "Gökyüzünün bugünkü notu hazır. Athena seni bekliyor ☾",
            "Bugünün temasına kısa bir göz atmaya ne dersin?",
            "Bir dakikalık gökyüzü molası: günlük yorumun hazır ✨",
        )
        val openAppIntent = PendingIntent.getActivity(
            applicationContext,
            2101,
            Intent(applicationContext, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
            },
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
        val notification = NotificationCompat.Builder(
            applicationContext,
            DAILY_REMINDER_CHANNEL_ID,
        )
            .setSmallIcon(R.drawable.ic_olimora_notification)
            .setColor(0xFF7B46AD.toInt())
            .setContentTitle("Olimora")
            .setContentText(messages[ZonedDateTime.now().dayOfYear % messages.size])
            .setContentIntent(openAppIntent)
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setAutoCancel(true)
            .build()
        NotificationManagerCompat.from(applicationContext).notify(2101, notification)
        return Result.success()
    }
}
