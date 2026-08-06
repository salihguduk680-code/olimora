package com.olimora.app.data

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

data class BigThreeResult(
    val sunSign: String,
    val sunDegree: Double,
    val moonSign: String,
    val moonDegree: Double,
    val ascendantSign: String,
    val ascendantDegree: Double,
    val positions: List<ChartPointResult>,
    val houses: List<HouseResult>,
    val aspects: List<AspectResult>,
)

data class ChartPointResult(
    val name: String,
    val sign: String,
    val degreeInSign: Double,
    val longitude: Double,
    val isRetrograde: Boolean,
    val house: Int?,
)

data class HouseResult(
    val number: Int,
    val sign: String,
    val degreeInSign: Double,
)

data class AspectResult(
    val bodyA: String,
    val bodyB: String,
    val type: String,
    val orb: Double,
)

data class AthenaResult(
    val interpretation: String,
    val source: String,
)

private const val NATAL_CHART_URL =
    "https://olimora-production.up.railway.app/api/v1/astrology/natal-chart/preview"
private const val ATHENA_URL =
    "https://olimora-production.up.railway.app/api/v1/athena/natal-chart/interpret"

suspend fun generateAthenaInterpretation(
    name: String,
    localDateTime: String,
    timezone: String,
    latitude: Double,
    longitude: Double,
    placeName: String,
): AthenaResult = withContext(Dispatchers.IO) {
    val request = chartRequest(
        localDateTime = localDateTime,
        timezone = timezone,
        latitude = latitude,
        longitude = longitude,
        placeName = placeName,
    ).put("name", name.ifBlank { "Gökyüzü Yolcusu" })
    val response = postJson(ATHENA_URL, request, readTimeout = 30_000)
    AthenaResult(
        interpretation = response.getString("interpretation"),
        source = response.getString("source"),
    )
}

suspend fun calculateBigThree(
    localDateTime: String,
    timezone: String,
    latitude: Double,
    longitude: Double,
    placeName: String,
): BigThreeResult = withContext(Dispatchers.IO) {
    val request = chartRequest(localDateTime, timezone, latitude, longitude, placeName)
    val response = postJson(NATAL_CHART_URL, request)
    val sun = response.getJSONObject("sun")
    val moon = response.getJSONObject("moon")
    val ascendant = response.getJSONObject("ascendant")
    val positionsJson = response.getJSONArray("positions")
    val housesJson = response.getJSONArray("houses")
    val aspectsJson = response.getJSONArray("aspects")
    BigThreeResult(
        sunSign = sun.getString("sign"),
        sunDegree = sun.getDouble("degree_in_sign"),
        moonSign = moon.getString("sign"),
        moonDegree = moon.getDouble("degree_in_sign"),
        ascendantSign = ascendant.getString("sign"),
        ascendantDegree = ascendant.getDouble("degree_in_sign"),
        positions = List(positionsJson.length()) { index ->
            val point = positionsJson.getJSONObject(index)
            ChartPointResult(
                name = point.getString("name"),
                sign = point.getString("sign"),
                degreeInSign = point.getDouble("degree_in_sign"),
                longitude = point.getDouble("longitude"),
                isRetrograde = point.optBoolean("is_retrograde", false),
                house = if (point.isNull("house")) null else point.getInt("house"),
            )
        },
        houses = List(housesJson.length()) { index ->
            val house = housesJson.getJSONObject(index)
            HouseResult(
                number = house.getInt("house_number"),
                sign = house.getString("sign"),
                degreeInSign = house.getDouble("degree_in_sign"),
            )
        },
        aspects = List(aspectsJson.length()) { index ->
            val aspect = aspectsJson.getJSONObject(index)
            AspectResult(
                bodyA = aspect.getString("body_a"),
                bodyB = aspect.getString("body_b"),
                type = aspect.getString("aspect_type"),
                orb = aspect.getDouble("orb"),
            )
        },
    )
}

private fun chartRequest(
    localDateTime: String,
    timezone: String,
    latitude: Double,
    longitude: Double,
    placeName: String,
): JSONObject = JSONObject()
    .put("local_datetime", localDateTime)
    .put("timezone_name", timezone)
    .put("latitude", latitude)
    .put("longitude", longitude)
    .put("place_name", placeName)
    .put("house_system", "P")

private fun postJson(url: String, request: JSONObject, readTimeout: Int = 20_000): JSONObject {
    val connection = (URL(url).openConnection() as HttpURLConnection).apply {
        requestMethod = "POST"
        connectTimeout = 10_000
        this.readTimeout = readTimeout
        doOutput = true
        setRequestProperty("Content-Type", "application/json; charset=utf-8")
        setRequestProperty("Accept", "application/json")
    }

    return try {
        connection.outputStream.bufferedWriter(Charsets.UTF_8).use { writer ->
            writer.write(request.toString())
        }

        val responseCode = connection.responseCode
        val responseText = (if (responseCode in 200..299) {
            connection.inputStream
        } else {
            connection.errorStream
        }).bufferedReader(Charsets.UTF_8).use { it.readText() }

        if (responseCode !in 200..299) {
            throw IllegalStateException("Sunucu $responseCode hatası verdi: $responseText")
        }

        JSONObject(responseText)
    } finally {
        connection.disconnect()
    }
}
