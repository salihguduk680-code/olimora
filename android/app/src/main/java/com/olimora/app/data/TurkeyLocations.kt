package com.olimora.app.data

import android.content.Context
import org.json.JSONObject

data class DistrictLocation(
    val id: Int,
    val name: String,
    val latitude: Double,
    val longitude: Double,
    val timezone: String,
)

data class ProvinceLocation(
    val id: Int,
    val name: String,
    val latitude: Double,
    val longitude: Double,
    val timezone: String,
    val districts: List<DistrictLocation>,
)

fun loadTurkeyLocations(context: Context): List<ProvinceLocation> {
    val json = context.assets
        .open("turkey_locations.json")
        .bufferedReader(Charsets.UTF_8)
        .use { it.readText() }
    val provinceArray = JSONObject(json).getJSONArray("provinces")

    return buildList(provinceArray.length()) {
        for (provinceIndex in 0 until provinceArray.length()) {
            val province = provinceArray.getJSONObject(provinceIndex)
            val districtArray = province.getJSONArray("districts")
            val districts = buildList(districtArray.length()) {
                for (districtIndex in 0 until districtArray.length()) {
                    val district = districtArray.getJSONObject(districtIndex)
                    add(
                        DistrictLocation(
                            id = district.getInt("id"),
                            name = district.getString("name"),
                            latitude = district.getDouble("latitude"),
                            longitude = district.getDouble("longitude"),
                            timezone = district.getString("timezone"),
                        ),
                    )
                }
            }
            add(
                ProvinceLocation(
                    id = province.getInt("id"),
                    name = province.getString("name"),
                    latitude = province.getDouble("latitude"),
                    longitude = province.getDouble("longitude"),
                    timezone = province.getString("timezone"),
                    districts = districts,
                ),
            )
        }
    }
}
