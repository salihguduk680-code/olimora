package com.olimora.app.data

import android.content.Context
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

private const val API_BASE = "https://olimora-production.up.railway.app/api/v1"

data class AccountSession(val token: String, val email: String)

data class SavedBirthProfile(
    val name: String,
    val localDateTime: String,
    val timezone: String,
    val latitude: Double,
    val longitude: Double,
    val placeName: String,
)

class SessionStore(context: Context) {
    private val preferences = context.getSharedPreferences("olimora_session", Context.MODE_PRIVATE)
    fun token(): String? = preferences.getString("token", null)
    fun email(): String? = preferences.getString("email", null)
    fun save(session: AccountSession) {
        preferences.edit().putString("token", session.token).putString("email", session.email).apply()
    }
    fun clear() = preferences.edit().clear().apply()
}

suspend fun authenticate(email: String, password: String, register: Boolean): AccountSession =
    withContext(Dispatchers.IO) {
        val endpoint = if (register) "register" else "login"
        val response = requestJson(
            "$API_BASE/auth/$endpoint",
            "POST",
            JSONObject().put("email", email.trim()).put("password", password),
        )
        AccountSession(response.getString("access_token"), response.getJSONObject("user").getString("email"))
    }

suspend fun fetchSavedBirthProfile(token: String): SavedBirthProfile? = withContext(Dispatchers.IO) {
    try {
        val response = requestJson("$API_BASE/me/birth-profile", "GET", token = token)
        SavedBirthProfile(
            name = response.getString("name"),
            localDateTime = response.getString("local_datetime"),
            timezone = response.getString("timezone_name"),
            latitude = response.getDouble("latitude"),
            longitude = response.getDouble("longitude"),
            placeName = response.getString("place_name"),
        )
    } catch (error: ApiException) {
        if (error.statusCode == 404) null else throw error
    }
}

suspend fun saveBirthProfile(
    token: String,
    name: String,
    localDateTime: String,
    timezone: String,
    latitude: Double,
    longitude: Double,
    placeName: String,
) = withContext(Dispatchers.IO) {
    requestJson(
        "$API_BASE/me/birth-profile",
        "PUT",
        JSONObject()
            .put("name", name)
            .put("local_datetime", localDateTime)
            .put("timezone_name", timezone)
            .put("latitude", latitude)
            .put("longitude", longitude)
            .put("place_name", placeName),
        token,
    )
    Unit
}

class ApiException(val statusCode: Int, message: String) : IllegalStateException(message)

private fun requestJson(
    url: String,
    method: String,
    body: JSONObject? = null,
    token: String? = null,
): JSONObject {
    val connection = (URL(url).openConnection() as HttpURLConnection).apply {
        requestMethod = method
        connectTimeout = 10_000
        readTimeout = 20_000
        setRequestProperty("Accept", "application/json")
        token?.let { setRequestProperty("Authorization", "Bearer $it") }
        if (body != null) {
            doOutput = true
            setRequestProperty("Content-Type", "application/json; charset=utf-8")
        }
    }
    return try {
        body?.let { request ->
            connection.outputStream.bufferedWriter(Charsets.UTF_8).use { it.write(request.toString()) }
        }
        val code = connection.responseCode
        val text = (if (code in 200..299) connection.inputStream else connection.errorStream)
            .bufferedReader(Charsets.UTF_8).use { it.readText() }
        if (code !in 200..299) {
            val detail = runCatching { JSONObject(text).optString("detail") }.getOrNull()
            throw ApiException(code, detail?.takeIf { it.isNotBlank() } ?: "Sunucu $code hatası verdi.")
        }
        JSONObject(text)
    } finally {
        connection.disconnect()
    }
}
