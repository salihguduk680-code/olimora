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

data class CountryLocation(
    val code: String,
    val name: String,
    val provinces: List<ProvinceLocation>,
)

fun loadCountries(context: Context): List<CountryLocation> = listOf(
    loadCountry(context, "turkey_locations.json"),
    loadCountry(context, "syria_locations.json"),
)

fun loadTurkeyLocations(context: Context): List<ProvinceLocation> {
    return loadCountry(context, "turkey_locations.json").provinces
}

private fun loadCountry(context: Context, assetName: String): CountryLocation {
    val json = context.assets
        .open(assetName)
        .bufferedReader(Charsets.UTF_8)
        .use { it.readText() }
    val root = JSONObject(json)
    val provinceArray = root.getJSONArray("provinces")

    val provinces = buildList(provinceArray.length()) {
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
    return CountryLocation(
        code = root.getString("country_code"),
        name = root.getString("country"),
        provinces = provinces,
    )
}
