package com.olimora.app

import android.app.DatePickerDialog
import android.app.TimePickerDialog
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.olimora.app.ui.theme.Gold
import com.olimora.app.ui.theme.OlimoraTheme
import com.olimora.app.ui.theme.PrimaryPurple
import com.olimora.app.ui.theme.SoftSurface
import com.olimora.app.data.loadTurkeyLocations
import com.olimora.app.data.AspectResult
import com.olimora.app.data.BigThreeResult
import com.olimora.app.data.ChartPointResult
import com.olimora.app.data.HouseResult
import com.olimora.app.data.DistrictLocation
import com.olimora.app.data.ProvinceLocation
import com.olimora.app.data.calculateBigThree
import com.olimora.app.data.generateAthenaInterpretation
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Locale

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            OlimoraTheme {
                OlimoraApp()
            }
        }
    }
}

private enum class OlimoraScreen { BirthForm, ChartResult }

@Composable
fun OlimoraApp() {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    val provinces = remember { loadTurkeyLocations(context) }
    var screen by remember { mutableStateOf(OlimoraScreen.BirthForm) }
    var name by remember { mutableStateOf("") }
    var birthDate by remember { mutableStateOf("") }
    var birthTime by remember { mutableStateOf("") }
    var country by remember { mutableStateOf("") }
    var province by remember { mutableStateOf<ProvinceLocation?>(null) }
    var district by remember { mutableStateOf<DistrictLocation?>(null) }
    var chartResult by remember { mutableStateOf<BigThreeResult?>(null) }
    var isCalculating by remember { mutableStateOf(false) }
    var calculationError by remember { mutableStateOf<String?>(null) }
    var athenaInterpretation by remember { mutableStateOf<String?>(null) }
    var isAthenaLoading by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .statusBarsPadding()
            .navigationBarsPadding(),
    ) {
        OlimoraHeader(step = if (screen == OlimoraScreen.BirthForm) "1 / 2" else "2 / 2")
        when (screen) {
            OlimoraScreen.BirthForm -> BirthFormScreen(
                name = name,
                onNameChange = { name = it },
                birthDate = birthDate,
                onBirthDateClick = {
                    val parts = birthDate.split(".").mapNotNull { it.toIntOrNull() }
                    val calendar = Calendar.getInstance()
                    val day = parts.getOrNull(0) ?: calendar.get(Calendar.DAY_OF_MONTH)
                    val month = (parts.getOrNull(1) ?: calendar.get(Calendar.MONTH) + 1) - 1
                    val year = parts.getOrNull(2) ?: calendar.get(Calendar.YEAR)
                    DatePickerDialog(context, { _, selectedYear, selectedMonth, selectedDay ->
                        birthDate = String.format(
                            Locale.ROOT,
                            "%02d.%02d.%04d",
                            selectedDay,
                            selectedMonth + 1,
                            selectedYear,
                        )
                    }, year, month, day).show()
                },
                birthTime = birthTime,
                onBirthTimeClick = {
                    val parts = birthTime.split(":").mapNotNull { it.toIntOrNull() }
                    TimePickerDialog(context, { _, hour, minute ->
                        birthTime = String.format(Locale.ROOT, "%02d:%02d", hour, minute)
                    }, parts.getOrNull(0) ?: 12, parts.getOrNull(1) ?: 0, true).show()
                },
                country = country,
                onCountryChange = {
                    country = it
                    province = null
                    district = null
                },
                province = province?.name.orEmpty(),
                provinceOptions = provinces.map { it.name },
                onProvinceChange = { selectedName ->
                    val selectedProvince = provinces.first { it.name == selectedName }
                    province = selectedProvince
                    district = null
                },
                district = district?.name.orEmpty(),
                districtOptions = province?.districts?.map { it.name }.orEmpty(),
                onDistrictChange = { selectedName ->
                    district = province?.districts?.first { it.name == selectedName }
                },
                isCalculating = isCalculating,
                calculationError = calculationError,
                onCreateChart = {
                    val localDateTime = toApiLocalDateTime(birthDate, birthTime)
                    val selectedDistrict = district
                    val selectedProvince = province
                    if (name.isBlank()) {
                        calculationError = "Lütfen adını yaz."
                    } else if (localDateTime == null) {
                        calculationError = "Lütfen geçerli doğum tarihi ve saati seç."
                    } else if (country.isBlank() || selectedProvince == null || selectedDistrict == null) {
                        calculationError = "Lütfen ülke, il ve ilçe seçimini tamamla."
                    } else {
                        calculationError = null
                        athenaInterpretation = null
                        isCalculating = true
                        coroutineScope.launch {
                            try {
                                val placeName = "${selectedDistrict.name}, ${selectedProvince.name}, Türkiye"
                                chartResult = calculateBigThree(
                                    localDateTime = localDateTime,
                                    timezone = selectedDistrict.timezone,
                                    latitude = selectedDistrict.latitude,
                                    longitude = selectedDistrict.longitude,
                                    placeName = placeName,
                                )
                                screen = OlimoraScreen.ChartResult
                                isAthenaLoading = true
                                try {
                                    athenaInterpretation = generateAthenaInterpretation(
                                        name = name,
                                        localDateTime = localDateTime,
                                        timezone = selectedDistrict.timezone,
                                        latitude = selectedDistrict.latitude,
                                        longitude = selectedDistrict.longitude,
                                        placeName = placeName,
                                    ).interpretation
                                } catch (_: Exception) {
                                    // Hesaplanan yerel özet, Athena kullanılamazsa güvenli yedek olarak kalır.
                                } finally {
                                    isAthenaLoading = false
                                }
                            } catch (error: Exception) {
                                calculationError = buildString {
                                    append("Astroloji sunucusuna ulaşılamadı.")
                                    error.message?.takeIf { it.isNotBlank() }?.let {
                                        append("\nTeknik neden: ")
                                        append(it.take(180))
                                    }
                                }
                            } finally {
                                isCalculating = false
                            }
                        }
                    }
                },
            )

            OlimoraScreen.ChartResult -> ChartResultScreen(
                name = name.ifBlank { "Gökyüzü Yolcusu" },
                birthDate = birthDate,
                birthTime = birthTime,
                place = "${district?.name}, ${province?.name}, Türkiye",
                chartResult = chartResult ?: return@Column,
                athenaInterpretation = athenaInterpretation,
                isAthenaLoading = isAthenaLoading,
                onEdit = { screen = OlimoraScreen.BirthForm },
            )
        }
    }
}

@Composable
private fun OlimoraHeader(step: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 22.dp, vertical = 16.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Box(
                modifier = Modifier
                    .size(36.dp)
                    .background(Color.Transparent, CircleShape)
                    .then(Modifier),
                contentAlignment = Alignment.Center,
            ) {
                Text(text = "✦", color = Gold, fontSize = 23.sp)
            }
            Text(
                text = "OLIMORA",
                modifier = Modifier.padding(start = 8.dp),
                color = MaterialTheme.colorScheme.onBackground,
                fontWeight = FontWeight.Medium,
                letterSpacing = 2.sp,
            )
        }
        Text(text = step, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

@Composable
private fun BirthFormScreen(
    name: String,
    onNameChange: (String) -> Unit,
    birthDate: String,
    onBirthDateClick: () -> Unit,
    birthTime: String,
    onBirthTimeClick: () -> Unit,
    country: String,
    onCountryChange: (String) -> Unit,
    province: String,
    provinceOptions: List<String>,
    onProvinceChange: (String) -> Unit,
    district: String,
    districtOptions: List<String>,
    onDistrictChange: (String) -> Unit,
    isCalculating: Boolean,
    calculationError: String?,
    onCreateChart: () -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 22.dp),
    ) {
        Text(
            text = "Gökyüzü hikâyen nerede başladı?",
            style = MaterialTheme.typography.headlineMedium,
            color = MaterialTheme.colorScheme.onBackground,
            fontWeight = FontWeight.Medium,
        )
        Text(
            text = "Doğum bilgilerini gir, haritanı birlikte oluşturalım.",
            modifier = Modifier.padding(top = 7.dp, bottom = 20.dp),
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        OlimoraField(label = "Adın", value = name, onValueChange = onNameChange)
        Spacer(Modifier.height(12.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            Box(Modifier.weight(1f)) {
                PickerField(
                    label = "Doğum tarihi",
                    value = birthDate,
                    onClick = onBirthDateClick,
                )
            }
            Box(Modifier.weight(1f)) {
                PickerField(
                    label = "Doğum saati",
                    value = birthTime,
                    onClick = onBirthTimeClick,
                )
            }
        }
        Spacer(Modifier.height(12.dp))
        SelectionField(
            label = "Ülke",
            value = country,
            options = listOf("Türkiye"),
            onSelected = onCountryChange,
        )
        Spacer(Modifier.height(12.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            Box(Modifier.weight(1f)) {
                SelectionField(
                    label = "İl",
                    value = province,
                    options = if (country.isBlank()) emptyList() else provinceOptions,
                    onSelected = onProvinceChange,
                )
            }
            Box(Modifier.weight(1f)) {
                SelectionField(
                    label = "İlçe",
                    value = district,
                    options = districtOptions,
                    onSelected = onDistrictChange,
                )
            }
        }

        Row(
            modifier = Modifier.padding(vertical = 17.dp),
            horizontalArrangement = Arrangement.spacedBy(9.dp),
        ) {
            Text(text = "☾", color = Gold)
            Text(
                text = "Saatini bilmiyorsan genel harita seçeneğini daha sonra ekleyeceğiz.",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                style = MaterialTheme.typography.bodySmall,
            )
        }

        Button(
            onClick = onCreateChart,
            enabled = !isCalculating,
            modifier = Modifier
                .fillMaxWidth()
                .height(52.dp),
            shape = RoundedCornerShape(14.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = PrimaryPurple,
                contentColor = Color.White,
            ),
        ) {
            Text(
                if (isCalculating) "Harita hesaplanıyor…" else "Haritamı oluştur",
                fontWeight = FontWeight.Medium,
            )
        }
        calculationError?.let { error ->
            Text(
                text = error,
                modifier = Modifier.padding(top = 10.dp),
                color = MaterialTheme.colorScheme.error,
                style = MaterialTheme.typography.bodySmall,
            )
        }
        SourceCodeLink()
        Spacer(Modifier.height(24.dp))
    }
}

@Composable
private fun PickerField(
    label: String,
    value: String,
    onClick: () -> Unit,
) {
    OutlinedButton(
        onClick = onClick,
        modifier = Modifier
            .fillMaxWidth()
            .height(56.dp),
        shape = RoundedCornerShape(12.dp),
        contentPadding = PaddingValues(horizontal = 14.dp),
    ) {
        Column(
            modifier = Modifier.weight(1f),
            horizontalAlignment = Alignment.Start,
        ) {
            Text(label, fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
            Text(
                text = value.ifBlank { "Seç" },
                color = if (value.isBlank()) {
                    MaterialTheme.colorScheme.onSurfaceVariant
                } else {
                    MaterialTheme.colorScheme.onSurface
                },
            )
        }
        Text("⌄", color = Gold, fontSize = 18.sp)
    }
}

@Composable
private fun OlimoraField(
    label: String,
    value: String,
    onValueChange: (String) -> Unit = {},
    readOnly: Boolean = false,
) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        modifier = Modifier.fillMaxWidth(),
        label = { Text(label) },
        singleLine = true,
        readOnly = readOnly,
        shape = RoundedCornerShape(12.dp),
        colors = OutlinedTextFieldDefaults.colors(
            focusedBorderColor = PrimaryPurple,
            unfocusedBorderColor = MaterialTheme.colorScheme.outline,
        ),
    )
}

@Composable
private fun SelectionField(
    label: String,
    value: String,
    options: List<String>,
    onSelected: (String) -> Unit,
) {
    var expanded by remember { mutableStateOf(false) }
    Box {
        OutlinedButton(
            onClick = { expanded = true },
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp),
            shape = RoundedCornerShape(12.dp),
            contentPadding = PaddingValues(horizontal = 14.dp),
        ) {
            Column(
                modifier = Modifier.weight(1f),
                horizontalAlignment = Alignment.Start,
            ) {
                Text(label, fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                Text(
                    text = value.ifBlank { "Seç" },
                    color = if (value.isBlank()) {
                        MaterialTheme.colorScheme.onSurfaceVariant
                    } else {
                        MaterialTheme.colorScheme.onSurface
                    },
                )
            }
            Text("⌄", color = Gold, fontSize = 18.sp)
        }
        DropdownMenu(
            expanded = expanded,
            onDismissRequest = { expanded = false },
        ) {
            options.forEach { option ->
                DropdownMenuItem(
                    text = { Text(option) },
                    onClick = {
                        onSelected(option)
                        expanded = false
                    },
                )
            }
        }
    }
}

@Composable
private fun ChartResultScreen(
    name: String,
    birthDate: String,
    birthTime: String,
    place: String,
    chartResult: BigThreeResult,
    athenaInterpretation: String?,
    isAthenaLoading: Boolean,
    onEdit: () -> Unit,
) {
    var detailsExpanded by remember { mutableStateOf(false) }
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 22.dp),
    ) {
        Text(
            text = "Doğum haritan hazır",
            style = MaterialTheme.typography.headlineMedium,
            color = MaterialTheme.colorScheme.onBackground,
            fontWeight = FontWeight.Medium,
        )
        Text(
            text = "Gökyüzünün doğduğun andaki matematiksel görünümü.",
            modifier = Modifier.padding(top = 7.dp, bottom = 18.dp),
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        Card(
            colors = CardDefaults.cardColors(containerColor = SoftSurface),
            shape = RoundedCornerShape(18.dp),
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Box(
                    modifier = Modifier
                        .size(64.dp)
                        .background(MaterialTheme.colorScheme.surface, CircleShape),
                    contentAlignment = Alignment.Center,
                ) {
                    Text("♓", color = Gold, fontSize = 32.sp)
                }
                Column(Modifier.padding(start = 15.dp)) {
                    Text(name, fontWeight = FontWeight.Medium, fontSize = 18.sp)
                    Text("$birthDate · $birthTime", color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text(place, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
        }

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 14.dp),
            horizontalArrangement = Arrangement.spacedBy(9.dp),
        ) {
            BigThreeCard(signSymbol(chartResult.sunSign), "Güneş", signName(chartResult.sunSign), chartResult.sunDegree, Modifier.weight(1f))
            BigThreeCard(signSymbol(chartResult.moonSign), "Ay", signName(chartResult.moonSign), chartResult.moonDegree, Modifier.weight(1f))
            BigThreeCard(signSymbol(chartResult.ascendantSign), "Yükselen", signName(chartResult.ascendantSign), chartResult.ascendantDegree, Modifier.weight(1f))
        }

        Text(
            text = "Athena’nın kısa yorumu",
            modifier = Modifier.padding(top = 22.dp, bottom = 10.dp),
            fontWeight = FontWeight.Medium,
        )
        Card(
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
            border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline),
            shape = RoundedCornerShape(14.dp),
        ) {
            Column(Modifier.padding(15.dp)) {
                Text(
                    if (isAthenaLoading) "Athena haritanı okuyor…" else "Haritandaki üç ana iz",
                    fontWeight = FontWeight.Medium,
                )
                Text(
                    text = athenaInterpretation ?: athenaShortInterpretation(chartResult),
                    modifier = Modifier.padding(top = 5.dp),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                Text(
                    text = "Astrolojik yorumlar eğlence ve öz farkındalık amaçlıdır.",
                    modifier = Modifier.padding(top = 10.dp),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    fontSize = 11.sp,
                )
            }
        }

        Row(
            modifier = Modifier.padding(top = 18.dp, bottom = if (detailsExpanded) 16.dp else 24.dp),
            horizontalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            OutlinedButton(
                onClick = onEdit,
                modifier = Modifier
                    .weight(1f)
                    .height(52.dp),
                shape = RoundedCornerShape(14.dp),
                contentPadding = PaddingValues(horizontal = 8.dp),
            ) {
                Text("Bilgileri düzenle", textAlign = TextAlign.Center)
            }
            Button(
                onClick = { detailsExpanded = !detailsExpanded },
                modifier = Modifier
                    .weight(1f)
                    .height(52.dp),
                shape = RoundedCornerShape(14.dp),
                colors = ButtonDefaults.buttonColors(containerColor = PrimaryPurple),
            ) {
                Text(if (detailsExpanded) "Detayları gizle" else "Detayları gör")
            }
        }

        if (detailsExpanded) {
            ChartDetailsSection(chartResult)
        }
        SourceCodeLink()
        Spacer(Modifier.height(24.dp))
    }
}

@Composable
private fun SourceCodeLink() {
    val context = LocalContext.current
    TextButton(
        onClick = {
            context.startActivity(
                Intent(
                    Intent.ACTION_VIEW,
                    Uri.parse("https://github.com/salihguduk680-code/olimora"),
                ),
            )
        },
        modifier = Modifier.fillMaxWidth(),
    ) {
        Text("Kaynak kodunu görüntüle (AGPL-3.0)")
    }
}

@Composable
private fun ChartDetailsSection(chart: BigThreeResult) {
    Text(
        text = "Athena’nın kullandığı hesaplama",
        style = MaterialTheme.typography.titleLarge,
        fontWeight = FontWeight.Medium,
    )
    Text(
        text = "Bunlar yorum değil; astroloji motorunun hesapladığı ham yerleşimlerdir.",
        modifier = Modifier.padding(top = 5.dp, bottom = 12.dp),
        color = MaterialTheme.colorScheme.onSurfaceVariant,
        style = MaterialTheme.typography.bodySmall,
    )

    DetailGroup(title = "Gezegen yerleşimleri") {
        chart.positions.forEachIndexed { index, point ->
            PlanetDetailRow(point)
            if (index != chart.positions.lastIndex) DetailSeparator()
        }
    }

    Spacer(Modifier.height(14.dp))
    DetailGroup(title = "12 ev") {
        chart.houses.forEachIndexed { index, house ->
            HouseDetailRow(house)
            if (index != chart.houses.lastIndex) DetailSeparator()
        }
    }

    Spacer(Modifier.height(14.dp))
    DetailGroup(title = "Önemli açılar") {
        if (chart.aspects.isEmpty()) {
            Text(
                text = "Seçili açı toleransına giren önemli bir açı bulunmadı.",
                modifier = Modifier.padding(14.dp),
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        } else {
            chart.aspects.forEachIndexed { index, aspect ->
                AspectDetailRow(aspect)
                if (index != chart.aspects.lastIndex) DetailSeparator()
            }
        }
    }
}

@Composable
private fun DetailGroup(title: String, content: @Composable () -> Unit) {
    Card(
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline),
        shape = RoundedCornerShape(14.dp),
    ) {
        Text(
            text = title,
            modifier = Modifier.padding(start = 14.dp, top = 13.dp, end = 14.dp, bottom = 6.dp),
            color = PrimaryPurple,
            fontWeight = FontWeight.SemiBold,
        )
        content()
    }
}

@Composable
private fun PlanetDetailRow(point: ChartPointResult) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 14.dp, vertical = 10.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(planetSymbol(point.name), color = Gold, fontSize = 23.sp)
        Column(Modifier.padding(start = 11.dp).weight(1f)) {
            Text(planetName(point.name), fontWeight = FontWeight.Medium)
            Text(
                text = "${signName(point.sign)} ${formatDegree(point.degreeInSign)}",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                style = MaterialTheme.typography.bodySmall,
            )
        }
        Column(horizontalAlignment = Alignment.End) {
            Text(
                text = point.house?.let { "$it. ev" } ?: "Ev yok",
                style = MaterialTheme.typography.bodySmall,
            )
            if (point.isRetrograde) {
                Text("Retro", color = PrimaryPurple, fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
            }
        }
    }
}

@Composable
private fun HouseDetailRow(house: HouseResult) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 14.dp, vertical = 9.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text("${house.number}. ev", modifier = Modifier.weight(1f), fontWeight = FontWeight.Medium)
        Text(
            text = "${signSymbol(house.sign)}  ${signName(house.sign)} ${formatDegree(house.degreeInSign)}",
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
private fun AspectDetailRow(aspect: AspectResult) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 14.dp, vertical = 10.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(Modifier.weight(1f)) {
            Text(
                text = "${planetName(aspect.bodyA)} – ${planetName(aspect.bodyB)}",
                fontWeight = FontWeight.Medium,
            )
            Text(
                text = aspectName(aspect.type),
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                style = MaterialTheme.typography.bodySmall,
            )
        }
        Text("orb ${formatDegree(aspect.orb)}", fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

@Composable
private fun DetailSeparator() {
    Box(
        Modifier
            .fillMaxWidth()
            .height(1.dp)
            .background(MaterialTheme.colorScheme.outline.copy(alpha = 0.35f)),
    )
}

@Composable
private fun BigThreeCard(
    symbol: String,
    label: String,
    sign: String,
    degree: Double,
    modifier: Modifier = Modifier,
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline),
        shape = RoundedCornerShape(14.dp),
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 13.dp, horizontal = 5.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(symbol, color = Gold, fontSize = 27.sp)
            Text(label, color = MaterialTheme.colorScheme.onSurfaceVariant, fontSize = 12.sp)
            Text(sign, modifier = Modifier.padding(top = 4.dp), fontWeight = FontWeight.Medium)
            Text(
                String.format(Locale.ROOT, "%.1f°", degree),
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                fontSize = 11.sp,
            )
        }
    }
}

private fun toApiLocalDateTime(date: String, time: String): String? {
    val input = SimpleDateFormat("dd.MM.yyyy HH:mm", Locale.ROOT).apply { isLenient = false }
    val parsed = input.parse("$date $time") ?: return null
    return SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.ROOT).format(parsed)
}

private fun signName(sign: String): String = mapOf(
    "aries" to "Koç", "taurus" to "Boğa", "gemini" to "İkizler",
    "cancer" to "Yengeç", "leo" to "Aslan", "virgo" to "Başak",
    "libra" to "Terazi", "scorpio" to "Akrep", "sagittarius" to "Yay",
    "capricorn" to "Oğlak", "aquarius" to "Kova", "pisces" to "Balık",
)[sign.lowercase()] ?: sign

private fun signSymbol(sign: String): String = mapOf(
    "aries" to "♈", "taurus" to "♉", "gemini" to "♊", "cancer" to "♋",
    "leo" to "♌", "virgo" to "♍", "libra" to "♎", "scorpio" to "♏",
    "sagittarius" to "♐", "capricorn" to "♑", "aquarius" to "♒", "pisces" to "♓",
)[sign.lowercase()] ?: "✦"

private fun planetName(name: String): String = mapOf(
    "sun" to "Güneş",
    "moon" to "Ay",
    "mercury" to "Merkür",
    "venus" to "Venüs",
    "mars" to "Mars",
    "jupiter" to "Jüpiter",
    "saturn" to "Satürn",
    "uranus" to "Uranüs",
    "neptune" to "Neptün",
    "pluto" to "Plüton",
    "ascendant" to "Yükselen",
)[name.lowercase()] ?: name.replaceFirstChar { it.uppercase() }

private fun planetSymbol(name: String): String = mapOf(
    "sun" to "☉",
    "moon" to "☽",
    "mercury" to "☿",
    "venus" to "♀",
    "mars" to "♂",
    "jupiter" to "♃",
    "saturn" to "♄",
    "uranus" to "♅",
    "neptune" to "♆",
    "pluto" to "♇",
    "ascendant" to "ASC",
)[name.lowercase()] ?: "✦"

private fun aspectName(type: String): String = mapOf(
    "conjunction" to "Kavuşum",
    "opposition" to "Karşıt",
    "trine" to "Üçgen",
    "square" to "Kare",
    "sextile" to "Sekstil",
)[type.lowercase()] ?: type.replaceFirstChar { it.uppercase() }

private fun formatDegree(value: Double): String =
    String.format(Locale.ROOT, "%.1f°", value)

private fun athenaShortInterpretation(chart: BigThreeResult): String {
    val sunThemes = mapOf(
        "aries" to "cesaret ve başlangıç enerjisi",
        "taurus" to "istikrar ve güven arayışı",
        "gemini" to "merak ve zihinsel hareketlilik",
        "cancer" to "aidiyet ve duygusal bağlar",
        "leo" to "yaratıcılık ve kendini ifade etme",
        "virgo" to "özen, düzen ve fayda üretme",
        "libra" to "denge, uyum ve ortaklık",
        "scorpio" to "derinlik ve dönüşüm",
        "sagittarius" to "keşif ve anlam arayışı",
        "capricorn" to "sorumluluk ve uzun vadeli hedefler",
        "aquarius" to "özgünlük ve bağımsız düşünce",
        "pisces" to "sezgi, hayal gücü ve duyarlılık",
    )
    val moonThemes = mapOf(
        "aries" to "hızlı ve doğrudan tepki verme",
        "taurus" to "huzur ve güvene ihtiyaç duyma",
        "gemini" to "duyguları konuşarak anlama",
        "cancer" to "yakınlık ve korunma ihtiyacı",
        "leo" to "görülme, sıcaklık ve takdir ihtiyacı",
        "virgo" to "duyguları düzenleyerek rahatlama",
        "libra" to "ilişkilerde uyum arama",
        "scorpio" to "yoğun ve derin hissetme",
        "sagittarius" to "özgürlük ve yenilikle canlanma",
        "capricorn" to "duyguları kontrollü yaşama",
        "aquarius" to "mesafe ve zihinsel alan ihtiyacı",
        "pisces" to "çevrendeki duyguları kolayca sezme",
    )
    val risingThemes = mapOf(
        "aries" to "enerjik ve girişken",
        "taurus" to "sakin ve güven veren",
        "gemini" to "meraklı ve konuşkan",
        "cancer" to "duyarlı ve temkinli",
        "leo" to "sıcak ve dikkat çekici",
        "virgo" to "ölçülü ve dikkatli",
        "libra" to "nazik ve uzlaştırıcı",
        "scorpio" to "gizemli ve kararlı",
        "sagittarius" to "neşeli ve açık sözlü",
        "capricorn" to "ciddi ve güvenilir",
        "aquarius" to "özgün ve bağımsız",
        "pisces" to "yumuşak ve sezgisel",
    )

    val sun = sunThemes[chart.sunSign] ?: "kendini keşfetme"
    val moon = moonThemes[chart.moonSign] ?: "duygularını anlama"
    val rising = risingThemes[chart.ascendantSign] ?: "kendine özgü"
    return "Güneş yerleşimin $sun temalarıyla ilişkilendirilir. " +
        "Ay yerleşimin, iç dünyanda $moon eğilimi gösterebileceğini anlatır. " +
        "Yükselenin ise ilk karşılaşmalarda $rising bir izlenim bırakabileceğini düşündürür."
}

@Preview(showBackground = true, widthDp = 390, heightDp = 760)
@Composable
private fun OlimoraPreview() {
    OlimoraTheme(darkTheme = true) {
        OlimoraApp()
    }
}
