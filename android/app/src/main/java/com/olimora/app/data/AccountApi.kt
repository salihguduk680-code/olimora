package com.olimora.app.data

import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Base64
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import org.json.JSONArray
import java.net.HttpURLConnection
import java.net.URL
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

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

data class DailySignReading(
    val date: String,
    val sign: String,
    val mainTheme: String,
    val relationships: String,
    val workMoney: String,
    val caution: String,
    val cached: Boolean,
)

data class SocialUser(
    val id: String,
    val displayName: String,
    val olimoraId: String,
    val unreadCount: Int,
    val isOnline: Boolean,
    val lastSeenAt: String?,
    val statusMessage: String?,
)
data class FriendRequest(val id: String, val user: SocialUser)
data class SocialOverview(
    val me: SocialUser,
    val friends: List<SocialUser>,
    val incoming: List<FriendRequest>,
    val outgoing: List<FriendRequest>,
    val totalUnread: Int,
)
data class DirectMessage(
    val id: String,
    val body: String,
    val isMine: Boolean,
    val createdAt: String,
    val readAt: String? = null,
)
data class SocialGroupMember(val user: SocialUser, val role: String)
data class SocialGroup(
    val id: String,
    val name: String,
    val ownerId: String,
    val members: List<SocialGroupMember>,
    val unreadCount: Int,
)
data class GroupMessage(
    val id: String,
    val sender: SocialUser,
    val body: String,
    val isMine: Boolean,
    val createdAt: String,
)

class SessionStore(context: Context) {
    private val preferences = context.getSharedPreferences("olimora_session", Context.MODE_PRIVATE)
    private val tokenCipher = SessionTokenCipher()

    fun token(): String? {
        preferences.getString("token_encrypted", null)?.let { encrypted ->
            return runCatching { tokenCipher.decrypt(encrypted) }
                .onFailure { clear() }
                .getOrNull()
        }
        val legacyToken = preferences.getString("token", null) ?: return null
        return runCatching {
            preferences.edit()
                .putString("token_encrypted", tokenCipher.encrypt(legacyToken))
                .remove("token")
                .apply()
            legacyToken
        }.onFailure { clear() }.getOrNull()
    }
    fun email(): String? = preferences.getString("email", null)
    fun save(session: AccountSession) {
        val encryptedToken = tokenCipher.encrypt(session.token)
        preferences.edit()
            .putString("token_encrypted", encryptedToken)
            .putString("email", session.email)
            .remove("token")
            .apply()
    }
    fun clear() = preferences.edit().clear().apply()
}

private class SessionTokenCipher {
    private val keyAlias = "olimora_session_token_v1"
    private val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }

    private fun secretKey(): SecretKey {
        (keyStore.getKey(keyAlias, null) as? SecretKey)?.let { return it }
        return KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore").run {
            init(
                KeyGenParameterSpec.Builder(
                    keyAlias,
                    KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT,
                )
                    .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                    .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                    .setRandomizedEncryptionRequired(true)
                    .build()
            )
            generateKey()
        }
    }

    fun encrypt(value: String): String {
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, secretKey())
        val combined = cipher.iv + cipher.doFinal(value.toByteArray(Charsets.UTF_8))
        return Base64.encodeToString(combined, Base64.NO_WRAP)
    }

    fun decrypt(value: String): String {
        val combined = Base64.decode(value, Base64.NO_WRAP)
        require(combined.size > 12) { "Encrypted session is invalid" }
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(
            Cipher.DECRYPT_MODE,
            secretKey(),
            GCMParameterSpec(128, combined.copyOfRange(0, 12)),
        )
        return cipher.doFinal(combined.copyOfRange(12, combined.size)).toString(Charsets.UTF_8)
    }
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

suspend fun requestDailySignReading(token: String): DailySignReading = withContext(Dispatchers.IO) {
    val response = requestJson("$API_BASE/athena/daily-sign", "POST", JSONObject(), token)
    DailySignReading(
        date = response.getString("reading_date"),
        sign = response.getString("sign"),
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
        me = parseSocialUser(response.getJSONObject("me")),
        friends = response.getJSONArray("friends").mapObjects(::parseSocialUser),
        incoming = response.getJSONArray("incoming").mapObjects(::parseFriendRequest),
        outgoing = response.getJSONArray("outgoing").mapObjects(::parseFriendRequest),
        totalUnread = response.optInt("total_unread", 0),
    )
}

suspend fun sendFriendRequest(token: String, olimoraId: String) = withContext(Dispatchers.IO) {
    requestJson(
        "$API_BASE/social/friend-requests",
        "POST",
        JSONObject().put("olimora_id", olimoraId.trim().lowercase().removePrefix("@")),
        token,
    )
    Unit
}

suspend fun updateSocialStatus(token: String, statusMessage: String?) = withContext(Dispatchers.IO) {
    requestJson(
        "$API_BASE/social/status",
        "PATCH",
        JSONObject().put("status_message", statusMessage ?: JSONObject.NULL),
        token,
    )
    Unit
}

suspend fun deleteAccount(token: String) = withContext(Dispatchers.IO) {
    requestNoContent("$API_BASE/auth/me", "DELETE", token)
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
                    readAt = item.optString("read_at").takeUnless { it.isBlank() || it == "null" },
                )
            }
    }

suspend fun sendDirectMessage(token: String, friendId: String, body: String): DirectMessage =
    withContext(Dispatchers.IO) {
        val item = requestJson(
            "$API_BASE/social/messages/$friendId",
            "POST",
            JSONObject().put("body", body.trim()),
            token,
        )
        DirectMessage(
            id = item.getString("id"),
            body = item.getString("body"),
            isMine = item.getBoolean("is_mine"),
            createdAt = item.getString("created_at"),
            readAt = item.optString("read_at").takeUnless { it.isBlank() || it == "null" },
        )
    }

suspend fun fetchGroups(token: String): List<SocialGroup> = withContext(Dispatchers.IO) {
    try {
        requestJsonArray("$API_BASE/social/groups", "GET", token = token)
            .mapObjects(::parseSocialGroup)
    } catch (error: ApiException) {
        // Eski backend sürümü çalışırken arkadaş ekranının tamamını bozma.
        if (error.statusCode == 404) emptyList() else throw error
    }
}

suspend fun createGroup(
    token: String,
    name: String,
    memberIds: List<String>,
): SocialGroup = withContext(Dispatchers.IO) {
    parseSocialGroup(
        requestJson(
            "$API_BASE/social/groups",
            "POST",
            JSONObject().put("name", name.trim()).put("member_ids", JSONArray(memberIds)),
            token,
        )
    )
}

suspend fun fetchGroupMessages(token: String, groupId: String): List<GroupMessage> =
    withContext(Dispatchers.IO) {
        requestJsonArray("$API_BASE/social/groups/$groupId/messages", "GET", token = token)
            .mapObjects(::parseGroupMessage)
    }

suspend fun sendGroupMessage(token: String, groupId: String, body: String) =
    withContext(Dispatchers.IO) {
        requestJson(
            "$API_BASE/social/groups/$groupId/messages",
            "POST",
            JSONObject().put("body", body.trim()),
            token,
        )
        Unit
    }

suspend fun leaveGroup(token: String, groupId: String) = withContext(Dispatchers.IO) {
    requestNoContent("$API_BASE/social/groups/$groupId/membership", "DELETE", token)
}

suspend fun registerPushInstallation(token: String, fid: String) = withContext(Dispatchers.IO) {
    requestJson(
        "$API_BASE/notifications/installation",
        "PUT",
        JSONObject().put("fid", fid).put("platform", "android"),
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
    olimoraId = item.getString("olimora_id"),
    unreadCount = item.optInt("unread_count", 0),
    isOnline = item.optBoolean("is_online", false),
    lastSeenAt = item.optString("last_seen_at").takeIf { it.isNotBlank() && it != "null" },
    statusMessage = item.optString("status_message").takeIf { it.isNotBlank() && it != "null" },
)

private fun parseFriendRequest(item: JSONObject) = FriendRequest(
    id = item.getString("id"),
    user = parseSocialUser(item.getJSONObject("user")),
)

private fun parseSocialGroup(item: JSONObject) = SocialGroup(
    id = item.getString("id"),
    name = item.getString("name"),
    ownerId = item.getString("owner_id"),
    members = item.getJSONArray("members").mapObjects { member ->
        SocialGroupMember(
            user = parseSocialUser(member.getJSONObject("user")),
            role = member.getString("role"),
        )
    },
    unreadCount = item.optInt("unread_count", 0),
)

private fun parseGroupMessage(item: JSONObject) = GroupMessage(
    id = item.getString("id"),
    sender = parseSocialUser(item.getJSONObject("sender")),
    body = item.getString("body"),
    isMine = item.getBoolean("is_mine"),
    createdAt = item.getString("created_at"),
)

private inline fun <T> JSONArray.mapObjects(transform: (JSONObject) -> T): List<T> =
    List(length()) { index -> transform(getJSONObject(index)) }
