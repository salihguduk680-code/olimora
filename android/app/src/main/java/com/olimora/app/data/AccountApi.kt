package com.olimora.app.data

import android.content.Context
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import org.json.JSONArray
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

data class DailyReading(
    val date: String,
    val mainTheme: String,
    val relationships: String,
    val workMoney: String,
    val caution: String,
    val cached: Boolean,
)

data class SocialUser(val id: String, val displayName: String, val email: String)
data class FriendRequest(val id: String, val user: SocialUser)
data class SocialOverview(
    val friends: List<SocialUser>,
    val incoming: List<FriendRequest>,
    val outgoing: List<FriendRequest>,
)
data class DirectMessage(val id: String, val body: String, val isMine: Boolean, val createdAt: String)

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

suspend fun requestDailyReading(token: String): DailyReading = withContext(Dispatchers.IO) {
    val response = requestJson("$API_BASE/athena/daily", "POST", JSONObject(), token)
    DailyReading(
        date = response.getString("reading_date"),
        mainTheme = response.getString("main_theme"),
        relationships = response.getString("relationships"),
        workMoney = response.getString("work_money"),
        caution = response.getString("caution"),
        cached = response.optBoolean("cached", false),
    )
}

suspend fun fetchSocialOverview(token: String): SocialOverview = withContext(Dispatchers.IO) {
    val response = requestJson("$API_BASE/social/overview", "GET", token = token)
    SocialOverview(
        friends = response.getJSONArray("friends").mapObjects(::parseSocialUser),
        incoming = response.getJSONArray("incoming").mapObjects(::parseFriendRequest),
        outgoing = response.getJSONArray("outgoing").mapObjects(::parseFriendRequest),
    )
}

suspend fun sendFriendRequest(token: String, email: String) = withContext(Dispatchers.IO) {
    requestJson(
        "$API_BASE/social/friend-requests",
        "POST",
        JSONObject().put("email", email.trim()),
        token,
    )
    Unit
}

suspend fun acceptFriendRequest(token: String, requestId: String) = withContext(Dispatchers.IO) {
    requestJson("$API_BASE/social/friend-requests/$requestId/accept", "POST", JSONObject(), token)
    Unit
}

suspend fun declineFriendRequest(token: String, requestId: String) = withContext(Dispatchers.IO) {
    requestNoContent("$API_BASE/social/friendships/$requestId", "DELETE", token)
}

suspend fun fetchMessages(token: String, friendId: String): List<DirectMessage> =
    withContext(Dispatchers.IO) {
        requestJsonArray("$API_BASE/social/messages/$friendId", "GET", token = token)
            .mapObjects { item ->
                DirectMessage(
                    id = item.getString("id"),
                    body = item.getString("body"),
                    isMine = item.getBoolean("is_mine"),
                    createdAt = item.getString("created_at"),
                )
            }
    }

suspend fun sendDirectMessage(token: String, friendId: String, body: String) =
    withContext(Dispatchers.IO) {
        requestJson(
            "$API_BASE/social/messages/$friendId",
            "POST",
            JSONObject().put("body", body.trim()),
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
): JSONObject = JSONObject(requestText(url, method, body, token))

private fun requestJsonArray(
    url: String,
    method: String,
    body: JSONObject? = null,
    token: String? = null,
): JSONArray = JSONArray(requestText(url, method, body, token))

private fun requestNoContent(url: String, method: String, token: String) {
    requestText(url, method, token = token)
}

private fun requestText(
    url: String,
    method: String,
    body: JSONObject? = null,
    token: String? = null,
): String {
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
        text.ifBlank { "{}" }
    } finally {
        connection.disconnect()
    }
}

private fun parseSocialUser(item: JSONObject) = SocialUser(
    id = item.getString("id"),
    displayName = item.getString("display_name"),
    email = item.getString("email"),
)

private fun parseFriendRequest(item: JSONObject) = FriendRequest(
    id = item.getString("id"),
    user = parseSocialUser(item.getJSONObject("user")),
)

private inline fun <T> JSONArray.mapObjects(transform: (JSONObject) -> T): List<T> =
    List(length()) { index -> transform(getJSONObject(index)) }
