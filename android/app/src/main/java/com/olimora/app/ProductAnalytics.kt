package com.olimora.app

import android.content.Context
import android.os.Bundle
import com.google.firebase.analytics.FirebaseAnalytics

/**
 * Opt-in product analytics. Event payloads must never contain names, e-mail,
 * birth data, message text, Olimora IDs, friend IDs, or location information.
 */
object ProductAnalytics {
    fun setEnabled(context: Context, enabled: Boolean) {
        FirebaseAnalytics.getInstance(context).setAnalyticsCollectionEnabled(enabled)
    }

    fun event(context: Context, name: String, enabled: Boolean, source: String? = null) {
        if (!enabled) return
        val params = source?.let { Bundle().apply { putString("source", it) } }
        FirebaseAnalytics.getInstance(context).logEvent(name, params)
    }
}
