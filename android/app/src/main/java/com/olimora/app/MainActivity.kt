package com.olimora.app

import android.Manifest
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.content.pm.ApplicationInfo
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.pulltorefresh.PullToRefreshBox
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.nativeCanvas
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.content.ContextCompat
import com.olimora.app.ui.theme.Gold
import com.olimora.app.ui.theme.OlimoraTheme
import com.olimora.app.ui.theme.PrimaryPurple
import com.olimora.app.ui.theme.SoftSurface
import com.olimora.app.data.AccountSession
import com.olimora.app.data.ApiException
import com.olimora.app.data.CountryLocation
import com.olimora.app.data.SessionStore
import com.olimora.app.data.authenticate
import com.olimora.app.data.fetchSavedBirthProfile
import com.olimora.app.data.loadCountries
import com.olimora.app.data.saveBirthProfile
import com.olimora.app.data.AspectResult
import com.olimora.app.data.BigThreeResult
import com.olimora.app.data.ChartPointResult
import com.olimora.app.data.HouseResult
import com.olimora.app.data.DistrictLocation
import com.olimora.app.data.DailySignReading
import com.olimora.app.data.DailyReading
import com.olimora.app.data.DirectMessage
import com.olimora.app.data.GroupMessage
import com.olimora.app.data.SocialGroup
import com.olimora.app.data.SocialOverview
import com.olimora.app.data.SocialUser
import com.olimora.app.data.ProvinceLocation
import com.olimora.app.data.calculateBigThree
import com.olimora.app.data.generateAthenaInterpretation
import com.olimora.app.data.requestDailySignReading
import com.olimora.app.data.requestDailyReading
import com.olimora.app.data.acceptFriendRequest
import com.olimora.app.data.declineFriendRequest
import com.olimora.app.data.deleteAccount
import com.olimora.app.data.fetchMessages
import com.olimora.app.data.fetchGroups
import com.olimora.app.data.fetchGroupMessages
import com.olimora.app.data.createGroup
import com.olimora.app.data.sendGroupMessage
import com.olimora.app.data.leaveGroup
import com.olimora.app.data.fetchSocialOverview
import com.olimora.app.data.sendDirectMessage
import com.olimora.app.data.sendFriendRequest
import com.olimora.app.data.updateSocialStatus
import kotlinx.coroutines.launch
import kotlinx.coroutines.delay
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Locale
import kotlin.math.PI
import kotlin.math.cos
import kotlin.math.min
import kotlin.math.sin
import kotlin.math.sqrt

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        createMessageNotificationChannel()
        if (
            Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
            ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) !=
            PackageManager.PERMISSION_GRANTED
        ) {
            requestPermissions(arrayOf(Manifest.permission.POST_NOTIFICATIONS), 1001)
        }
        enableEdgeToEdge()
        setContent {
            OlimoraTheme {
                val isDebuggable = applicationInfo.flags and ApplicationInfo.FLAG_DEBUGGABLE != 0
                if (isDebuggable && intent.getBooleanExtra("settings_design_preview", false)) {
                    SettingsScreen(
                        accountEmail = "salih@olimora.app",
                        token = null,
                        profileName = "Salih",
                        sunSign = "pisces",
                        moonSign = "pisces",
                        ascendantSign = "libra",
                        onEditProfile = {},
                        onAbout = {},
                        onLogout = {},
                        onAccountDeleted = {},
                        betaPremiumEnabled = true,
                        onBetaPremiumChange = {},
                        onBack = {},
                    )
                } else if (isDebuggable && intent.getBooleanExtra("premium_design_preview", false)) {
                    ChartResultScreen(
                        name = "Salih",
                        birthDate = "12.03.2002",
                        birthTime = "20:00",
                        place = "Vakfıkebir, Trabzon, Türkiye",
                        chartResult = BigThreeResult(
                            sunSign = "pisces",
                            sunDegree = 22.0,
                            moonSign = "pisces",
                            moonDegree = 7.5,
                            ascendantSign = "libra",
                            ascendantDegree = 23.3,
                            positions = emptyList(),
                            houses = emptyList(),
                            aspects = emptyList(),
                        ),
                        athenaInterpretation = "Sezgisel ve yaratıcı yönün, insan ilişkilerindeki denge arayışınla birleşiyor. Haritan; duyguları güçlü hissettiğini fakat dışarıya daha sakin ve uzlaştırıcı bir izlenim verdiğini anlatıyor.",
                        isAthenaLoading = false,
                        dailySignReading = null,
                        dailySignReadingLoading = false,
                        dailySignReadingError = null,
                        onRequestDailySignReading = {},
                        betaPremiumEnabled = true,
                        premiumDailyReading = null,
                        premiumDailyReadingLoading = false,
                        premiumDailyReadingError = null,
                        onRequestPremiumDailyReading = {},
                    )
                } else if (
                    isDebuggable &&
                    intent.getBooleanExtra("chat_design_preview", false)
                ) {
                    ConversationScreen(
                        token = "",
                        friend = SocialUser(
                            id = "preview-friend",
                            displayName = "Elif",
                            olimoraId = "oli_preview",
                            unreadCount = 0,
                            isOnline = true,
                            lastSeenAt = null,
                            statusMessage = "Gökyüzünü dinliyor ✦",
                        ),
                        onBack = {},
                        previewMessages = listOf(
                            DirectMessage("preview-1", "Bugünkü yorumuna baktın mı? ✨", false, "2026-08-11T15:07:00Z"),
                            DirectMessage("preview-2", "Evet 😄", true, "2026-08-11T15:08:00Z"),
                            DirectMessage("preview-3", "🌙", false, "2026-08-11T15:09:00Z"),
                            DirectMessage("preview-4", "Çok iyi olmuş!", true, "2026-08-11T15:10:00Z"),
                        ),
                    )
                } else {
                    OlimoraApp()
                }
            }
        }
    }

    private fun createMessageNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                MESSAGE_CHANNEL_ID,
                "Arkadaş mesajları",
                NotificationManager.IMPORTANCE_DEFAULT,
            ).apply { description = "Olimora arkadaşlarından gelen yeni mesajlar" }
            getSystemService(NotificationManager::class.java).createNotificationChannel(channel)
            val reminderChannel = NotificationChannel(
                DAILY_REMINDER_CHANNEL_ID,
                "Günlük Olimora hatırlatmaları",
                NotificationManager.IMPORTANCE_DEFAULT,
            ).apply { description = "Günlük yorumuna bakmayı hatırlatan öğle bildirimi" }
            getSystemService(NotificationManager::class.java).createNotificationChannel(reminderChannel)
        }
    }
}

private const val MESSAGE_CHANNEL_ID = "olimora_messages"
internal const val DAILY_REMINDER_CHANNEL_ID = "olimora_daily_reminders"

internal fun Context.showMessageNotification(
    unreadCount: Int,
    title: String = "Olimora'da yeni mesajın var",
    body: String = "$unreadCount okunmamış mesaj seni bekliyor.",
) {
    if (
        Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
        ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) !=
        PackageManager.PERMISSION_GRANTED
    ) return
    val openAppIntent = PendingIntent.getActivity(
        this,
        2001,
        Intent(this, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
        },
        PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
    )
    val notification = NotificationCompat.Builder(this, MESSAGE_CHANNEL_ID)
        .setSmallIcon(R.drawable.ic_olimora_notification)
        .setColor(0xFF7B46AD.toInt())
        .setContentTitle(title)
        .setContentText(body)
        .setPriority(NotificationCompat.PRIORITY_DEFAULT)
        .setContentIntent(openAppIntent)
        .setAutoCancel(true)
        .build()
    NotificationManagerCompat.from(this).notify(2001, notification)
}

private enum class OlimoraScreen { Login, Loading, BirthForm, ChartResult, Settings, About }

@Composable
fun OlimoraApp() {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    val countries = remember { loadCountries(context) }
    val sessionStore = remember { SessionStore(context) }
    var authToken by remember { mutableStateOf(sessionStore.token()) }
    var screen by remember {
        mutableStateOf(if (authToken == null) OlimoraScreen.Login else OlimoraScreen.Loading)
    }
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
    var dailySignReading by remember { mutableStateOf<DailySignReading?>(null) }
    var dailySignReadingLoading by remember { mutableStateOf(false) }
    var dailySignReadingError by remember { mutableStateOf<String?>(null) }
    var premiumDailyReading by remember { mutableStateOf<DailyReading?>(null) }
    var premiumDailyReadingLoading by remember { mutableStateOf(false) }
    var premiumDailyReadingError by remember { mutableStateOf<String?>(null) }
    var unreadMessageCount by remember { mutableStateOf(0) }
    var isConversationOpen by remember { mutableStateOf(false) }
    var lastNotifiedUnreadCount by remember { mutableStateOf(0) }
    val experiencePreferences = remember {
        context.getSharedPreferences("olimora_experience", Context.MODE_PRIVATE)
    }
    var onboardingStep by remember {
        mutableStateOf(if (experiencePreferences.getBoolean("intro_seen", false)) -1 else 0)
    }
    var betaPremiumEnabled by remember {
        mutableStateOf(experiencePreferences.getBoolean("beta_premium_enabled", false))
    }

    LaunchedEffect(authToken) {
        if (authToken == null) {
            cancelDailyOlimoraReminder(context)
        } else {
            scheduleDailyOlimoraReminder(context)
        }
    }

    val selectedCountry: CountryLocation? = countries.firstOrNull { it.name == country }
    val provinces = selectedCountry?.provinces.orEmpty()

    BackHandler(
        enabled = !isConversationOpen && when (screen) {
            OlimoraScreen.Settings, OlimoraScreen.About -> true
            OlimoraScreen.BirthForm -> chartResult != null
            else -> false
        },
    ) {
        screen = OlimoraScreen.ChartResult
    }

    LaunchedEffect(authToken) {
        val token = authToken ?: return@LaunchedEffect
        screen = OlimoraScreen.Loading
        val saved = try {
            fetchSavedBirthProfile(token)
        } catch (error: ApiException) {
            if (error.statusCode == 401) {
                sessionStore.clear()
                authToken = null
                screen = OlimoraScreen.Login
            }
            null
        } catch (_: Exception) {
            null
        }
        if (saved == null) {
            if (authToken != null) screen = OlimoraScreen.BirthForm
            return@LaunchedEffect
        }
        saved?.let { saved ->
            name = saved.name
            val dateTimeParts = saved.localDateTime.take(16).split("T")
            if (dateTimeParts.size == 2) {
                val date = dateTimeParts[0].split("-")
                if (date.size == 3) birthDate = "${date[2]}.${date[1]}.${date[0]}"
                birthTime = dateTimeParts[1]
            }
            val matchCountry = countries.firstOrNull { candidate ->
                candidate.provinces.any { item ->
                    item.districts.any { location ->
                        kotlin.math.abs(location.latitude - saved.latitude) < 0.0001 &&
                            kotlin.math.abs(location.longitude - saved.longitude) < 0.0001
                    }
                }
            }
            val matchProvince = matchCountry?.provinces?.firstOrNull { item ->
                item.districts.any { location ->
                    kotlin.math.abs(location.latitude - saved.latitude) < 0.0001 &&
                        kotlin.math.abs(location.longitude - saved.longitude) < 0.0001
                }
            }
            country = matchCountry?.name.orEmpty()
            province = matchProvince
            district = matchProvince?.districts?.firstOrNull { location ->
                kotlin.math.abs(location.latitude - saved.latitude) < 0.0001 &&
                    kotlin.math.abs(location.longitude - saved.longitude) < 0.0001
            }
            isCalculating = true
            calculationError = null
            try {
                chartResult = calculateBigThree(
                    token = token,
                    localDateTime = saved.localDateTime,
                    timezone = saved.timezone,
                    latitude = saved.latitude,
                    longitude = saved.longitude,
                    placeName = saved.placeName,
                )
                screen = OlimoraScreen.ChartResult
                isAthenaLoading = true
                athenaInterpretation = runCatching {
                    generateAthenaInterpretation(
                        token = token,
                        name = saved.name,
                        localDateTime = saved.localDateTime,
                        timezone = saved.timezone,
                        latitude = saved.latitude,
                        longitude = saved.longitude,
                        placeName = saved.placeName,
                    ).interpretation
                }.getOrNull()
                isAthenaLoading = false
            } catch (error: Exception) {
                calculationError = error.message
                screen = OlimoraScreen.BirthForm
            } finally {
                isCalculating = false
            }
        }
    }

    LaunchedEffect(authToken) {
        val token = authToken ?: return@LaunchedEffect
        val firebasePushReady = runCatching {
            registerFirebaseInstallation(context, token)
        }.getOrDefault(false)
        while (true) {
            runCatching { fetchSocialOverview(token) }.getOrNull()?.let { overview ->
                val groupUnread = runCatching { fetchGroups(token).sumOf { it.unreadCount } }
                    .getOrDefault(0)
                val totalUnread = overview.totalUnread + groupUnread
                unreadMessageCount = totalUnread
                if (!firebasePushReady && totalUnread > lastNotifiedUnreadCount) {
                    context.showMessageNotification(totalUnread)
                }
                lastNotifiedUnreadCount = totalUnread
            }
            delay(10_000)
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .statusBarsPadding()
            .navigationBarsPadding(),
    ) {
        if (!isConversationOpen) OlimoraHeader(
            step = when (screen) {
                OlimoraScreen.Login -> "HESAP"
                OlimoraScreen.Loading -> ""
                OlimoraScreen.BirthForm -> ""
                OlimoraScreen.ChartResult -> ""
                OlimoraScreen.Settings -> ""
                OlimoraScreen.About -> ""
            },
            accountEmail = sessionStore.email(),
            onReturnToChart = if (
                chartResult != null && screen != OlimoraScreen.ChartResult && screen != OlimoraScreen.Login
            ) {
                { screen = OlimoraScreen.ChartResult }
            } else {
                null
            },
            onSettings = if (screen == OlimoraScreen.Login || screen == OlimoraScreen.Loading) null else {
                { screen = OlimoraScreen.Settings }
            },
        )
        when (screen) {
            OlimoraScreen.Login -> AccountScreen(
                onAuthenticated = { session ->
                    sessionStore.save(session)
                    authToken = session.token
                    screen = OlimoraScreen.Loading
                },
            )

            OlimoraScreen.Loading -> LoadingScreen()

            OlimoraScreen.BirthForm -> BirthFormScreen(
                isEditing = chartResult != null,
                name = name,
                onNameChange = { name = it },
                birthDate = birthDate,
                onBirthDateChange = { input ->
                    birthDate = formatDateInput(previous = birthDate, value = input)
                    calculationError = null
                },
                birthTime = birthTime,
                onBirthTimeChange = { input ->
                    birthTime = formatTimeInput(previous = birthTime, value = input)
                    calculationError = null
                },
                country = country,
                countryOptions = countries.map { it.name },
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
                                val placeName = "${selectedDistrict.name}, ${selectedProvince.name}, $country"
                                chartResult = calculateBigThree(
                                    token = authToken ?: error("Oturum gerekli."),
                                    localDateTime = localDateTime,
                                    timezone = selectedDistrict.timezone,
                                    latitude = selectedDistrict.latitude,
                                    longitude = selectedDistrict.longitude,
                                    placeName = placeName,
                                )
                                authToken?.let { token ->
                                    runCatching {
                                        saveBirthProfile(
                                            token = token,
                                            name = name,
                                            localDateTime = localDateTime,
                                            timezone = selectedDistrict.timezone,
                                            latitude = selectedDistrict.latitude,
                                            longitude = selectedDistrict.longitude,
                                            placeName = placeName,
                                        )
                                    }
                                }
                                dailySignReading = null
                                dailySignReadingError = null
                                screen = OlimoraScreen.ChartResult
                                isAthenaLoading = true
                                try {
                                    athenaInterpretation = generateAthenaInterpretation(
                                        token = authToken ?: error("Oturum gerekli."),
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

            OlimoraScreen.ChartResult -> {
                val pagerState = rememberPagerState(pageCount = { 3 })
                BackHandler(
                    enabled = !isConversationOpen && pagerState.currentPage != 0,
                ) {
                    coroutineScope.launch { pagerState.animateScrollToPage(0) }
                }
                Column(Modifier.fillMaxSize()) {
                    if (!isConversationOpen) {
                        ChartPagerNavigation(
                            selectedPage = pagerState.currentPage,
                            unreadCount = unreadMessageCount,
                            onSelectPage = { page ->
                                coroutineScope.launch { pagerState.animateScrollToPage(page) }
                            },
                        )
                    }
                    HorizontalPager(
                        state = pagerState,
                        modifier = Modifier.weight(1f),
                        userScrollEnabled = !isConversationOpen,
                    ) { page ->
                        if (page == 0) {
                            ChartResultScreen(
                            name = name.ifBlank { "Gökyüzü Yolcusu" },
                            birthDate = birthDate,
                            birthTime = birthTime,
                            place = "${district?.name}, ${province?.name}, $country",
                            chartResult = chartResult ?: return@HorizontalPager,
                            athenaInterpretation = athenaInterpretation,
                            isAthenaLoading = isAthenaLoading,
                            dailySignReading = dailySignReading,
                            dailySignReadingLoading = dailySignReadingLoading,
                            dailySignReadingError = dailySignReadingError,
                            onRequestDailySignReading = {
                                authToken?.let { token ->
                                    dailySignReadingLoading = true
                                    dailySignReadingError = null
                                    coroutineScope.launch {
                                        try {
                                            dailySignReading = requestDailySignReading(token)
                                        } catch (error: Exception) {
                                            dailySignReadingError = error.message
                                                ?: "Günlük burç yorumu şu anda hazırlanamadı."
                                        } finally {
                                            dailySignReadingLoading = false
                                        }
                                    }
                                }
                            },
                            betaPremiumEnabled = betaPremiumEnabled,
                            premiumDailyReading = premiumDailyReading,
                            premiumDailyReadingLoading = premiumDailyReadingLoading,
                            premiumDailyReadingError = premiumDailyReadingError,
                            onRequestPremiumDailyReading = {
                                authToken?.let { token ->
                                    premiumDailyReadingLoading = true
                                    premiumDailyReadingError = null
                                    coroutineScope.launch {
                                        try {
                                            premiumDailyReading = requestDailyReading(token)
                                        } catch (error: Exception) {
                                            premiumDailyReadingError = error.message
                                                ?: "Kişisel Premium yorum şu anda hazırlanamadı."
                                        } finally {
                                            premiumDailyReadingLoading = false
                                        }
                                    }
                                }
                            },
                            )
                        } else if (page == 1) {
                            ChartWheelScreen(chartResult ?: return@HorizontalPager)
                        } else {
                            authToken?.let { token ->
                                SocialScreen(
                                    token = token,
                                    onConversationChanged = { isConversationOpen = it },
                                )
                            }
                        }
                    }
                }
            }

            OlimoraScreen.Settings -> SettingsScreen(
                accountEmail = sessionStore.email(),
                token = authToken,
                profileName = name.ifBlank { "Gökyüzü Yolcusu" },
                sunSign = chartResult?.sunSign,
                moonSign = chartResult?.moonSign,
                ascendantSign = chartResult?.ascendantSign,
                onEditProfile = { screen = OlimoraScreen.BirthForm },
                onAbout = { screen = OlimoraScreen.About },
                onLogout = {
                    sessionStore.clear()
                    authToken = null
                    screen = OlimoraScreen.Login
                },
                onAccountDeleted = {
                    sessionStore.clear()
                    authToken = null
                    chartResult = null
                    screen = OlimoraScreen.Login
                },
                betaPremiumEnabled = betaPremiumEnabled,
                onBetaPremiumChange = { enabled ->
                    betaPremiumEnabled = enabled
                    experiencePreferences.edit().putBoolean("beta_premium_enabled", enabled).apply()
                    if (!enabled) {
                        premiumDailyReading = null
                        premiumDailyReadingError = null
                    }
                },
                onBack = {
                    screen = if (chartResult == null) OlimoraScreen.BirthForm else OlimoraScreen.ChartResult
                },
            )

            OlimoraScreen.About -> AboutScreen(onBack = {
                screen = if (chartResult == null) OlimoraScreen.BirthForm else OlimoraScreen.ChartResult
            })
        }
    }
    if (screen == OlimoraScreen.ChartResult && onboardingStep >= 0) {
        OlimoraOnboardingDialog(
            step = onboardingStep,
            onNext = {
                if (onboardingStep < 2) {
                    onboardingStep += 1
                } else {
                    experiencePreferences.edit().putBoolean("intro_seen", true).apply()
                    onboardingStep = -1
                }
            },
            onSkip = {
                experiencePreferences.edit().putBoolean("intro_seen", true).apply()
                onboardingStep = -1
            },
        )
    }
}

@Composable
private fun OlimoraOnboardingDialog(step: Int, onNext: () -> Unit, onSkip: () -> Unit) {
    val pages = listOf(
        Triple("✦", "Haritan hep seninle", "Doğum bilgilerin hesabında saklanır. Güneş, Ay ve yükselen sonuçlarına yeniden bilgi girmeden ulaşabilirsin."),
        Triple("☾", "Her gün yeni bir gökyüzü", "Günlük yorumun yalnızca istediğinde hazırlanır. Kalıcı harita özetiyle günlük yorumu artık kolayca ayırt edebilirsin."),
        Triple("☺", "Arkadaşların bir kaydırma uzakta", "Harita ekranını sola kaydırarak arkadaşlarına, mesajlarına ve yeni isteklerine geçebilirsin."),
    )
    val page = pages[step.coerceIn(pages.indices)]
    AlertDialog(
        onDismissRequest = {},
        icon = {
            Box(
                modifier = Modifier.size(58.dp).background(PrimaryPurple.copy(alpha = 0.13f), CircleShape),
                contentAlignment = Alignment.Center,
            ) { Text(page.first, color = Gold, fontSize = 27.sp) }
        },
        title = { Text(page.second, textAlign = TextAlign.Center, fontWeight = FontWeight.SemiBold) },
        text = {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(page.third, textAlign = TextAlign.Center, color = MaterialTheme.colorScheme.onSurfaceVariant)
                Row(
                    modifier = Modifier.padding(top = 18.dp),
                    horizontalArrangement = Arrangement.spacedBy(7.dp),
                ) {
                    repeat(3) { index ->
                        Box(
                            Modifier.size(if (index == step) 20.dp else 7.dp, 7.dp)
                                .background(
                                    if (index == step) PrimaryPurple else MaterialTheme.colorScheme.outline,
                                    CircleShape,
                                )
                        )
                    }
                }
            }
        },
        confirmButton = {
            Button(onClick = onNext, colors = ButtonDefaults.buttonColors(containerColor = PrimaryPurple)) {
                Text(if (step == 2) "Olimora’yı keşfet" else "Devam")
            }
        },
        dismissButton = { TextButton(onClick = onSkip) { Text("Atla") } },
        shape = RoundedCornerShape(24.dp),
    )
}

@Composable
private fun AccountScreen(onAuthenticated: (AccountSession) -> Unit) {
    val coroutineScope = rememberCoroutineScope()
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var passwordConfirmation by remember { mutableStateOf("") }
    var registerMode by remember { mutableStateOf(true) }
    var loading by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 22.dp),
        verticalArrangement = Arrangement.Center,
    ) {
        Text(
            text = if (registerMode) "Gökyüzündeki yerini kaydet" else "Tekrar hoş geldin",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Medium,
        )
        Text(
            text = "Doğum bilgilerin hesabında saklansın; her seferinde yeniden girmek zorunda kalma.",
            modifier = Modifier.padding(top = 8.dp, bottom = 22.dp),
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        OutlinedTextField(
            value = email,
            onValueChange = {
                email = it.trim().lowercase()
                error = null
            },
            label = { Text("E-posta") },
            singleLine = true,
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
            modifier = Modifier.fillMaxWidth(),
        )
        Spacer(Modifier.height(12.dp))
        OutlinedTextField(
            value = password,
            onValueChange = {
                password = it
                error = null
            },
            label = {
                Text(
                    if (registerMode) "Şifre (10+ karakter, harf ve rakam)"
                    else "Şifre"
                )
            },
            singleLine = true,
            visualTransformation = PasswordVisualTransformation(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
            modifier = Modifier.fillMaxWidth(),
        )
        if (registerMode) {
            Spacer(Modifier.height(12.dp))
            OutlinedTextField(
                value = passwordConfirmation,
                onValueChange = {
                    passwordConfirmation = it
                    error = null
                },
                label = { Text("Şifreyi tekrar yaz") },
                singleLine = true,
                visualTransformation = PasswordVisualTransformation(),
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                isError = passwordConfirmation.isNotEmpty() && password != passwordConfirmation,
                supportingText = {
                    if (passwordConfirmation.isNotEmpty() && password != passwordConfirmation) {
                        Text("Şifreler henüz eşleşmiyor.")
                    }
                },
                modifier = Modifier.fillMaxWidth(),
            )
        }
        error?.let { message ->
            StatusNotice(message = message, isError = true, modifier = Modifier.padding(top = 10.dp))
        }
        Button(
            onClick = {
                val registrationPasswordValid = password.length >= 10 &&
                    password.any(Char::isLetter) && password.any(Char::isDigit)
                if (!email.contains("@") || (!registerMode && password.length < 8)) {
                    error = "Geçerli bir e-posta ve şifre gir."
                } else if (registerMode && !registrationPasswordValid) {
                    error = "Yeni şifren en az 10 karakter, bir harf ve bir rakam içermeli."
                } else if (registerMode && password != passwordConfirmation) {
                    error = "Yazdığın iki şifre birbiriyle aynı değil."
                } else {
                    loading = true
                    error = null
                    coroutineScope.launch {
                        try {
                            onAuthenticated(authenticate(email.trim(), password, registerMode))
                        } catch (failure: Exception) {
                            error = failure.message ?: "Hesaba bağlanılamadı."
                        } finally {
                            loading = false
                        }
                    }
                }
            },
            enabled = !loading,
            modifier = Modifier.fillMaxWidth().padding(top = 18.dp).height(52.dp),
            shape = RoundedCornerShape(14.dp),
            colors = ButtonDefaults.buttonColors(containerColor = PrimaryPurple),
        ) {
            Text(if (loading) "Bağlanıyor…" else if (registerMode) "Hesap oluştur" else "Giriş yap")
        }
        TextButton(
            onClick = {
                registerMode = !registerMode
                passwordConfirmation = ""
                error = null
            },
            modifier = Modifier.align(Alignment.CenterHorizontally),
        ) {
            Text(if (registerMode) "Zaten hesabın var mı? Giriş yap" else "Hesabın yok mu? Kayıt ol")
        }
        Text(
            text = "Şifren tek yönlü olarak korunur ve açık biçimde saklanmaz.",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            textAlign = TextAlign.Center,
            modifier = Modifier.fillMaxWidth().padding(top = 8.dp),
        )
    }
}

@Composable
private fun OlimoraHeader(
    step: String,
    accountEmail: String?,
    onReturnToChart: (() -> Unit)?,
    onSettings: (() -> Unit)?,
) {
    var profileMenuExpanded by remember { mutableStateOf(false) }
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
        if (onSettings == null) {
            Text(text = step, color = MaterialTheme.colorScheme.onSurfaceVariant)
        } else {
            Box {
                TextButton(onClick = { profileMenuExpanded = true }) {
                    Box(
                        modifier = Modifier
                            .size(34.dp)
                            .background(PrimaryPurple.copy(alpha = 0.12f), CircleShape),
                        contentAlignment = Alignment.Center,
                    ) {
                        Text(
                            text = accountEmail?.firstOrNull()?.uppercase() ?: "👤",
                            color = PrimaryPurple,
                            fontWeight = FontWeight.Bold,
                            fontSize = 15.sp,
                        )
                    }
                }
                DropdownMenu(
                    expanded = profileMenuExpanded,
                    onDismissRequest = { profileMenuExpanded = false },
                ) {
                    accountEmail?.let {
                        DropdownMenuItem(
                            text = {
                                Column {
                                    Text("Hesabım", fontWeight = FontWeight.Medium)
                                    Text(it, style = MaterialTheme.typography.bodySmall)
                                }
                            },
                            onClick = {},
                            enabled = false,
                        )
                    }
                    onReturnToChart?.let { returnToChart ->
                        DropdownMenuItem(
                            text = { Text("Haritama dön") },
                            onClick = {
                                profileMenuExpanded = false
                                returnToChart()
                            },
                        )
                    }
                    onSettings?.let { openSettings ->
                        DropdownMenuItem(
                            text = { Text("Ayarlar") },
                            onClick = {
                                profileMenuExpanded = false
                                openSettings()
                            },
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun LoadingScreen() {
    Box(modifier = Modifier.fillMaxSize().padding(28.dp), contentAlignment = Alignment.Center) {
        Card(
            colors = CardDefaults.cardColors(containerColor = PrimaryPurple.copy(alpha = 0.08f)),
            shape = RoundedCornerShape(24.dp),
        ) {
            Column(
                modifier = Modifier.padding(horizontal = 30.dp, vertical = 26.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                Box(contentAlignment = Alignment.Center) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(52.dp),
                        color = PrimaryPurple,
                        strokeWidth = 3.dp,
                    )
                    Text("✦", color = Gold, fontSize = 22.sp)
                }
                Text("Athena gökyüzünü hazırlıyor", modifier = Modifier.padding(top = 10.dp), fontWeight = FontWeight.SemiBold)
                Text(
                    "Haritan ve kayıtlı bilgilerin getiriliyor…",
                    modifier = Modifier.padding(top = 5.dp),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    textAlign = TextAlign.Center,
                    style = MaterialTheme.typography.bodySmall,
                )
            }
        }
    }
}

@Composable
private fun BirthFormScreen(
    isEditing: Boolean,
    name: String,
    onNameChange: (String) -> Unit,
    birthDate: String,
    onBirthDateChange: (String) -> Unit,
    birthTime: String,
    onBirthTimeChange: (String) -> Unit,
    country: String,
    countryOptions: List<String>,
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
    var showDatePicker by remember { mutableStateOf(false) }
    var showTimePicker by remember { mutableStateOf(false) }
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 22.dp),
    ) {
        Text(
            text = if (isEditing) "Profil bilgilerin" else "Gökyüzü hikâyen nerede başladı?",
            style = MaterialTheme.typography.headlineMedium,
            color = MaterialTheme.colorScheme.onBackground,
            fontWeight = FontWeight.Medium,
        )
        Text(
            text = if (isEditing) {
                "Bilgilerini güncellediğinde haritanı yeniden hesaplayacağız."
            } else {
                "Doğum bilgilerini bir kez gir; hesabında güvenle saklayalım."
            },
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
                    placeholder = "GG.AA.YYYY",
                    onValueChange = onBirthDateChange,
                    onClick = { showDatePicker = true },
                )
            }
            Box(Modifier.weight(1f)) {
                PickerField(
                    label = "Doğum saati",
                    value = birthTime,
                    placeholder = "SS:DD",
                    onValueChange = onBirthTimeChange,
                    onClick = { showTimePicker = true },
                )
            }
        }
        Spacer(Modifier.height(12.dp))
        SelectionField(
            label = "Ülke",
            value = country,
            options = countryOptions,
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
                if (isCalculating) {
                    "Harita hesaplanıyor…"
                } else if (isEditing) {
                    "Kaydet ve haritayı yenile"
                } else {
                    "Haritamı oluştur"
                },
                fontWeight = FontWeight.Medium,
            )
        }
        calculationError?.let { error ->
            StatusNotice(
                message = error,
                isError = true,
                modifier = Modifier.padding(top = 10.dp),
            )
        }
        Spacer(Modifier.height(24.dp))
    }
    if (showDatePicker) {
        OlimoraDatePickerDialog(
            initialValue = birthDate,
            onDismiss = { showDatePicker = false },
            onConfirm = {
                onBirthDateChange(it)
                showDatePicker = false
            },
        )
    }
    if (showTimePicker) {
        OlimoraTimePickerDialog(
            initialValue = birthTime,
            onDismiss = { showTimePicker = false },
            onConfirm = {
                onBirthTimeChange(it)
                showTimePicker = false
            },
        )
    }
}

@Composable
private fun PickerField(
    label: String,
    value: String,
    placeholder: String,
    onValueChange: (String) -> Unit,
    onClick: () -> Unit,
) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        modifier = Modifier
            .fillMaxWidth()
            .heightIn(min = 66.dp),
        label = { Text(label, maxLines = 1) },
        placeholder = { Text(placeholder, maxLines = 1) },
        textStyle = MaterialTheme.typography.bodyMedium.copy(
            lineHeight = MaterialTheme.typography.bodyMedium.fontSize * 1.25f,
        ),
        singleLine = true,
        shape = RoundedCornerShape(12.dp),
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
        trailingIcon = {
            TextButton(onClick = onClick, contentPadding = PaddingValues(4.dp)) {
                Text("Seç", color = PrimaryPurple, fontSize = 12.sp, fontWeight = FontWeight.Medium)
            }
        },
        colors = OutlinedTextFieldDefaults.colors(
            focusedBorderColor = PrimaryPurple,
            unfocusedBorderColor = MaterialTheme.colorScheme.outline,
        ),
    )
}

@Composable
private fun OlimoraDatePickerDialog(
    initialValue: String,
    onDismiss: () -> Unit,
    onConfirm: (String) -> Unit,
) {
    val today = remember { Calendar.getInstance() }
    val parts = initialValue.split(".").mapNotNull(String::toIntOrNull)
    var day by remember { mutableStateOf(parts.getOrNull(0) ?: today.get(Calendar.DAY_OF_MONTH)) }
    var month by remember { mutableStateOf(parts.getOrNull(1) ?: today.get(Calendar.MONTH) + 1) }
    var year by remember { mutableStateOf(parts.getOrNull(2) ?: today.get(Calendar.YEAR)) }
    val maximumDay = remember(month, year) {
        Calendar.getInstance().apply {
            set(Calendar.YEAR, year.coerceIn(1900, today.get(Calendar.YEAR)))
            set(Calendar.MONTH, month.coerceIn(1, 12) - 1)
        }.getActualMaximum(Calendar.DAY_OF_MONTH)
    }
    LaunchedEffect(maximumDay) {
        if (day > maximumDay) day = maximumDay
    }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Doğum tarihini seç", fontWeight = FontWeight.SemiBold) },
        text = {
            Column {
                Text(
                    "Değerleri yazabilir veya − / + düğmeleriyle değiştirebilirsin.",
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    style = MaterialTheme.typography.bodySmall,
                )
                Row(
                    modifier = Modifier.fillMaxWidth().padding(top = 16.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    NumberStepper("Gün", day, 1..maximumDay, Modifier.weight(1f)) { day = it }
                    NumberStepper("Ay", month, 1..12, Modifier.weight(1f)) { month = it }
                    NumberStepper(
                        "Yıl",
                        year,
                        1900..today.get(Calendar.YEAR),
                        Modifier.weight(1.25f),
                    ) { year = it }
                }
                Text(
                    String.format(Locale.ROOT, "%02d.%02d.%04d", day, month, year),
                    modifier = Modifier.fillMaxWidth().padding(top = 18.dp),
                    color = PrimaryPurple,
                    fontWeight = FontWeight.SemiBold,
                    textAlign = TextAlign.Center,
                )
            }
        },
        confirmButton = {
            Button(
                onClick = {
                    onConfirm(String.format(Locale.ROOT, "%02d.%02d.%04d", day, month, year))
                },
                colors = ButtonDefaults.buttonColors(containerColor = PrimaryPurple),
            ) { Text("Tarihi kullan") }
        },
        dismissButton = { TextButton(onClick = onDismiss) { Text("Vazgeç") } },
        shape = RoundedCornerShape(24.dp),
    )
}

@Composable
private fun OlimoraTimePickerDialog(
    initialValue: String,
    onDismiss: () -> Unit,
    onConfirm: (String) -> Unit,
) {
    val parts = initialValue.split(":").mapNotNull(String::toIntOrNull)
    var hour by remember { mutableStateOf(parts.getOrNull(0)?.coerceIn(0, 23) ?: 12) }
    var minute by remember { mutableStateOf(parts.getOrNull(1)?.coerceIn(0, 59) ?: 0) }
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Doğum saatini seç", fontWeight = FontWeight.SemiBold) },
        text = {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(
                    "24 saat düzeninde saat ve dakikayı belirle.",
                    modifier = Modifier.fillMaxWidth(),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    style = MaterialTheme.typography.bodySmall,
                )
                Row(
                    modifier = Modifier.fillMaxWidth().padding(top = 16.dp),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    NumberStepper("Saat", hour, 0..23, Modifier.weight(1f)) { hour = it }
                    NumberStepper("Dakika", minute, 0..59, Modifier.weight(1f)) { minute = it }
                }
                Text(
                    String.format(Locale.ROOT, "%02d:%02d", hour, minute),
                    modifier = Modifier.padding(top = 18.dp),
                    color = PrimaryPurple,
                    fontWeight = FontWeight.SemiBold,
                    fontSize = 24.sp,
                )
            }
        },
        confirmButton = {
            Button(
                onClick = { onConfirm(String.format(Locale.ROOT, "%02d:%02d", hour, minute)) },
                colors = ButtonDefaults.buttonColors(containerColor = PrimaryPurple),
            ) { Text("Saati kullan") }
        },
        dismissButton = { TextButton(onClick = onDismiss) { Text("Vazgeç") } },
        shape = RoundedCornerShape(24.dp),
    )
}

@Composable
private fun NumberStepper(
    label: String,
    value: Int,
    range: IntRange,
    modifier: Modifier = Modifier,
    onValueChange: (Int) -> Unit,
) {
    var inputText by remember { mutableStateOf(value.toString()) }
    LaunchedEffect(value) { inputText = value.toString() }
    Column(modifier, horizontalAlignment = Alignment.CenterHorizontally) {
        Text(label, color = MaterialTheme.colorScheme.onSurfaceVariant, fontSize = 11.sp)
        OutlinedTextField(
            value = inputText,
            onValueChange = { input ->
                val digits = input.filter(Char::isDigit).take(range.last.toString().length)
                inputText = digits
                digits.toIntOrNull()?.takeIf { it in range }?.let {
                    onValueChange(it)
                }
            },
            modifier = Modifier.fillMaxWidth().padding(top = 4.dp),
            singleLine = true,
            textStyle = MaterialTheme.typography.bodyLarge.copy(textAlign = TextAlign.Center),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            shape = RoundedCornerShape(12.dp),
        )
        Row(
            modifier = Modifier.fillMaxWidth().padding(top = 5.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
        ) {
            TextButton(
                onClick = { onValueChange(if (value <= range.first) range.last else value - 1) },
                contentPadding = PaddingValues(2.dp),
            ) { Text("−", fontSize = 20.sp) }
            TextButton(
                onClick = { onValueChange(if (value >= range.last) range.first else value + 1) },
                contentPadding = PaddingValues(2.dp),
            ) { Text("+", fontSize = 20.sp) }
        }
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
    modifier: Modifier = Modifier,
) {
    var expanded by remember { mutableStateOf(false) }
    var query by remember { mutableStateOf("") }
    val filteredOptions = remember(options, query) {
        if (query.isBlank()) options else options.filter {
            it.contains(query.trim(), ignoreCase = true)
        }
    }
    Box(modifier) {
        OutlinedButton(
            onClick = {
                query = ""
                expanded = true
            },
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
    if (expanded) {
        AlertDialog(
            onDismissRequest = { expanded = false },
            title = { Text("$label seç") },
            text = {
                Column {
                    OutlinedTextField(
                        value = query,
                        onValueChange = { query = it },
                        modifier = Modifier.fillMaxWidth(),
                        label = { Text("Ara") },
                        placeholder = { Text("Yazarak seçenekleri filtrele") },
                        singleLine = true,
                        shape = RoundedCornerShape(12.dp),
                    )
                    LazyColumn(
                        modifier = Modifier.fillMaxWidth().heightIn(max = 360.dp).padding(top = 8.dp),
                    ) {
                        if (filteredOptions.isEmpty()) {
                            item {
                                Text(
                                    "Eşleşen seçenek bulunamadı.",
                                    modifier = Modifier.padding(vertical = 18.dp),
                                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                                )
                            }
                        }
                        items(filteredOptions.size) { index ->
                            val option = filteredOptions[index]
                            TextButton(
                                onClick = {
                                    onSelected(option)
                                    expanded = false
                                },
                                modifier = Modifier.fillMaxWidth(),
                                contentPadding = PaddingValues(horizontal = 10.dp, vertical = 9.dp),
                            ) {
                                Text(
                                    option,
                                    modifier = Modifier.fillMaxWidth(),
                                    color = MaterialTheme.colorScheme.onSurface,
                                    textAlign = TextAlign.Start,
                                )
                            }
                        }
                    }
                }
            },
            confirmButton = { TextButton(onClick = { expanded = false }) { Text("Kapat") } },
            shape = RoundedCornerShape(22.dp),
        )
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
    dailySignReading: DailySignReading?,
    dailySignReadingLoading: Boolean,
    dailySignReadingError: String?,
    onRequestDailySignReading: () -> Unit,
    betaPremiumEnabled: Boolean,
    premiumDailyReading: DailyReading?,
    premiumDailyReadingLoading: Boolean,
    premiumDailyReadingError: String?,
    onRequestPremiumDailyReading: () -> Unit,
) {
    val context = LocalContext.current
    var detailsExpanded by remember { mutableStateOf(false) }
    val now = remember { Calendar.getInstance() }
    val greeting = when (now.get(Calendar.HOUR_OF_DAY)) {
        in 5..11 -> "Günaydın"
        in 12..17 -> "İyi günler"
        else -> "İyi akşamlar"
    }
    val todayLabel = remember {
        SimpleDateFormat("d MMMM EEEE", Locale.forLanguageTag("tr-TR")).format(now.time)
    }
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 22.dp),
    ) {
        Card(
            modifier = Modifier.fillMaxWidth().padding(bottom = 18.dp),
            colors = CardDefaults.cardColors(containerColor = Color.Transparent),
            shape = RoundedCornerShape(22.dp),
        ) {
            Box(
                Modifier.fillMaxWidth()
                    .background(
                        Brush.linearGradient(
                            listOf(PrimaryPurple.copy(alpha = 0.18f), Gold.copy(alpha = 0.10f))
                        )
                    )
                    .padding(18.dp)
            ) {
                Column {
                    Text(
                        "$greeting, ${name.substringBefore(" ")}",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.SemiBold,
                    )
                    Text(
                        todayLabel.replaceFirstChar { it.uppercase() },
                        modifier = Modifier.padding(top = 4.dp),
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    Text(
                        "Gökyüzündeki yerin hazır.",
                        modifier = Modifier.padding(top = 12.dp),
                        color = PrimaryPurple,
                        fontWeight = FontWeight.Medium,
                    )
                }
            }
        }

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
                    Text(name, color = Color.White, fontWeight = FontWeight.Medium, fontSize = 18.sp)
                    Text("$birthDate · $birthTime", color = Color.White.copy(alpha = 0.72f))
                    Text(place, color = Color.White.copy(alpha = 0.72f))
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
            text = "Doğum haritanın özeti",
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
                    if (isAthenaLoading) "Athena haritanı okuyor…" else "Athena’nın temel okuması · Ücretsiz",
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

        Text(
            text = "Bugünün yorumu",
            modifier = Modifier.padding(top = 22.dp, bottom = 6.dp),
            fontWeight = FontWeight.Medium,
            fontSize = 20.sp,
        )
        Text(
            text = "Yalnızca Güneş burcun olan ${signName(chartResult.sunSign)} için hazırlanır ve her gün yenilenir.",
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            style = MaterialTheme.typography.bodySmall,
        )
        if (dailySignReading == null) {
            Button(
                onClick = onRequestDailySignReading,
                enabled = !dailySignReadingLoading,
                modifier = Modifier.fillMaxWidth().padding(top = 12.dp).height(52.dp),
                shape = RoundedCornerShape(14.dp),
                colors = ButtonDefaults.buttonColors(containerColor = PrimaryPurple),
            ) {
                Text(if (dailySignReadingLoading) "Bugünün yorumu hazırlanıyor…" else "${signName(chartResult.sunSign)} günlük yorumumu göster")
            }
            dailySignReadingError?.let { message ->
                StatusNotice(
                    message = message,
                    isError = true,
                    modifier = Modifier.padding(top = 10.dp),
                    actionLabel = "Tekrar dene",
                    onAction = onRequestDailySignReading,
                )
            }
        } else {
            DailyReadingCard("Günün teması", dailySignReading.mainTheme)
            DailyReadingCard("Aşk ve ilişkiler", dailySignReading.relationships)
            DailyReadingCard("İş ve para", dailySignReading.workMoney)
            DailyReadingCard("Dikkat", dailySignReading.caution)
            Text(
                text = "${dailySignReading.date} · Genel burç yorumu · Yatırım tavsiyesi değildir.",
                modifier = Modifier.padding(top = 8.dp),
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                style = MaterialTheme.typography.bodySmall,
            )
            OutlinedButton(
                onClick = {
                    shareDailySignReading(
                        context = context,
                        name = name,
                        sign = signName(chartResult.sunSign),
                        reading = dailySignReading,
                    )
                },
                modifier = Modifier.fillMaxWidth().padding(top = 12.dp).height(50.dp),
                shape = RoundedCornerShape(14.dp),
            ) {
                Text("✦  Yorumumu paylaş")
            }
        }

        PremiumInsightCard(
            betaPremiumEnabled = betaPremiumEnabled,
            reading = premiumDailyReading,
            loading = premiumDailyReadingLoading,
            error = premiumDailyReadingError,
            onRequestReading = onRequestPremiumDailyReading,
        )
        ReadingHistoryPreview(todayReady = dailySignReading != null)

        Button(
            onClick = { detailsExpanded = !detailsExpanded },
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 18.dp, bottom = if (detailsExpanded) 16.dp else 24.dp)
                .height(52.dp),
            shape = RoundedCornerShape(14.dp),
            colors = ButtonDefaults.buttonColors(containerColor = PrimaryPurple),
        ) {
            Text(if (detailsExpanded) "Detayları gizle" else "Detayları gör")
        }

        if (detailsExpanded) {
            ChartDetailsSection(chartResult)
        }
        Spacer(Modifier.height(24.dp))
    }
}

private fun shareDailySignReading(
    context: Context,
    name: String,
    sign: String,
    reading: DailySignReading,
) {
    val shareText = buildString {
        append("✦ OLIMORA · ")
        append(sign.uppercase(Locale.forLanguageTag("tr-TR")))
        append("\n\n")
        append(name.substringBefore(" "))
        append(" için bugünün teması:\n")
        append(reading.mainTheme)
        append("\n\nAşk ve ilişkiler:\n")
        append(reading.relationships)
        append("\n\nAstrolojik yorumlar eğlence ve öz farkındalık amaçlıdır.")
    }
    val intent = Intent(Intent.ACTION_SEND).apply {
        type = "text/plain"
        putExtra(Intent.EXTRA_SUBJECT, "Olimora günlük yorumum")
        putExtra(Intent.EXTRA_TEXT, shareText)
    }
    context.startActivity(Intent.createChooser(intent, "Olimora yorumunu paylaş"))
}

@Composable
private fun DailyReadingCard(title: String, text: String) {
    Card(
        modifier = Modifier.fillMaxWidth().padding(top = 10.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline),
        shape = RoundedCornerShape(14.dp),
    ) {
        Column(Modifier.padding(15.dp)) {
            Text(title, color = PrimaryPurple, fontWeight = FontWeight.Medium)
            Text(
                text = text,
                modifier = Modifier.padding(top = 5.dp),
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun PremiumInsightCard(
    betaPremiumEnabled: Boolean,
    reading: DailyReading?,
    loading: Boolean,
    error: String?,
    onRequestReading: () -> Unit,
) {
    Text(
        text = "Athena Premium",
        modifier = Modifier.padding(top = 26.dp, bottom = 8.dp),
        fontWeight = FontWeight.SemiBold,
        fontSize = 20.sp,
    )
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(22.dp),
        border = BorderStroke(1.dp, Gold.copy(alpha = 0.65f)),
        colors = CardDefaults.cardColors(containerColor = Color.Transparent),
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    Brush.linearGradient(
                        colors = listOf(
                            PrimaryPurple.copy(alpha = 0.16f),
                            Gold.copy(alpha = 0.10f),
                            MaterialTheme.colorScheme.surface,
                        )
                    )
                )
                .padding(18.dp),
        ) {
            Column {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .background(Gold.copy(alpha = 0.18f), RoundedCornerShape(50.dp))
                            .padding(horizontal = 10.dp, vertical = 5.dp),
                    ) {
                        Text(
                            "✦ PREMIUM",
                            color = Color(0xFF9A6812),
                            fontWeight = FontWeight.Bold,
                            fontSize = 11.sp,
                        )
                    }
                    Spacer(Modifier.width(9.dp))
                    Text("Sana özel derin okuma", fontWeight = FontWeight.SemiBold)
                }
                Text(
                    "Doğum haritan, güncel gezegen hareketleri ve kişisel temaların birlikte yorumlanır.",
                    modifier = Modifier.padding(top = 13.dp, bottom = 12.dp),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                PremiumBenefit("Kişisel günlük ve haftalık analiz")
                PremiumBenefit("İlişki, iş ve duygusal enerji başlıkları")
                PremiumBenefit("Daha uzun Athena yorumları")
                OutlinedButton(
                    onClick = onRequestReading,
                    enabled = betaPremiumEnabled && !loading,
                    modifier = Modifier.fillMaxWidth().padding(top = 14.dp).height(50.dp),
                    shape = RoundedCornerShape(14.dp),
                ) {
                    Text(
                        when {
                            loading -> "Athena kişisel yorumunu hazırlıyor…"
                            betaPremiumEnabled && reading == null -> "Beta Premium yorumumu hazırla"
                            betaPremiumEnabled -> "Premium yorumumu yenile"
                            else -> "Premium yakında"
                        }
                    )
                }
                Text(
                    if (betaPremiumEnabled) {
                        "Beta Premium test erişimin açık. Bu özellik senden ücret almaz."
                    } else {
                        "Ödeme sistemi açılmadan senden ücret alınmaz."
                    },
                    modifier = Modifier.fillMaxWidth().padding(top = 8.dp),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    fontSize = 11.sp,
                    textAlign = TextAlign.Center,
                )
                error?.let { message ->
                    StatusNotice(
                        message = message,
                        isError = true,
                        modifier = Modifier.padding(top = 10.dp),
                        actionLabel = "Tekrar dene",
                        onAction = onRequestReading,
                    )
                }
                reading?.let { premium ->
                    Text(
                        "Bugüne özel kişisel okuman",
                        modifier = Modifier.padding(top = 18.dp, bottom = 2.dp),
                        color = PrimaryPurple,
                        fontWeight = FontWeight.SemiBold,
                    )
                    PremiumReadingSection("Ana tema", premium.mainTheme)
                    PremiumReadingSection("İlişkiler", premium.relationships)
                    PremiumReadingSection("İş ve para", premium.workMoney)
                    PremiumReadingSection("Dikkat etmen gereken", premium.caution)
                    Text(
                        "${premium.date} · Kişisel doğum haritana göre hazırlanmıştır.",
                        modifier = Modifier.padding(top = 9.dp),
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        fontSize = 11.sp,
                    )
                }
            }
        }
    }
}

@Composable
private fun PremiumReadingSection(title: String, body: String) {
    Column(Modifier.padding(top = 12.dp)) {
        Text(title, fontWeight = FontWeight.Medium, style = MaterialTheme.typography.bodySmall)
        Text(
            body,
            modifier = Modifier.padding(top = 3.dp),
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            style = MaterialTheme.typography.bodySmall,
        )
    }
}

@Composable
private fun PremiumBenefit(text: String) {
    Row(
        modifier = Modifier.padding(vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text("✦", color = Gold, fontSize = 13.sp)
        Text(
            text,
            modifier = Modifier.padding(start = 9.dp),
            color = MaterialTheme.colorScheme.onSurface,
            style = MaterialTheme.typography.bodySmall,
        )
    }
}

@Composable
private fun ReadingHistoryPreview(todayReady: Boolean) {
    val days = remember {
        List(7) { offset ->
            Calendar.getInstance().apply { add(Calendar.DAY_OF_YEAR, offset - 6) }
        }
    }
    Text(
        "Yorum geçmişin",
        modifier = Modifier.padding(top = 26.dp, bottom = 5.dp),
        fontWeight = FontWeight.SemiBold,
        fontSize = 20.sp,
    )
    Text(
        "Bugün ücretsiz; önceki günlerin arşivi Premium ile açılır.",
        color = MaterialTheme.colorScheme.onSurfaceVariant,
        style = MaterialTheme.typography.bodySmall,
    )
    Row(
        modifier = Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()).padding(top = 12.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        days.forEachIndexed { index, day ->
            val isToday = index == days.lastIndex
            Card(
                colors = CardDefaults.cardColors(
                    containerColor = if (isToday) PrimaryPurple.copy(alpha = 0.12f)
                    else MaterialTheme.colorScheme.surface
                ),
                border = BorderStroke(
                    1.dp,
                    if (isToday) PrimaryPurple.copy(alpha = 0.6f) else MaterialTheme.colorScheme.outline,
                ),
                shape = RoundedCornerShape(15.dp),
            ) {
                Column(
                    modifier = Modifier.width(66.dp).padding(vertical = 11.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                ) {
                    Text(SimpleDateFormat("EEE", Locale.forLanguageTag("tr-TR")).format(day.time), fontSize = 11.sp)
                    Text(day.get(Calendar.DAY_OF_MONTH).toString(), fontWeight = FontWeight.SemiBold, fontSize = 18.sp)
                    Text(
                        if (isToday && todayReady) "✓" else if (isToday) "Bugün" else "🔒",
                        color = if (isToday) PrimaryPurple else MaterialTheme.colorScheme.onSurfaceVariant,
                        fontSize = 10.sp,
                    )
                }
            }
        }
    }
}

@Composable
private fun ChartPagerNavigation(
    selectedPage: Int,
    unreadCount: Int,
    onSelectPage: (Int) -> Unit,
) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 18.dp, vertical = 4.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        listOf("Athena" to 0, "Harita" to 1, "Arkadaşlar" to 2).forEach { (label, page) ->
            val selected = selectedPage == page
            TextButton(
                onClick = { onSelectPage(page) },
                modifier = Modifier.weight(1f),
                colors = ButtonDefaults.textButtonColors(
                    containerColor = if (selected) PrimaryPurple.copy(alpha = 0.12f) else Color.Transparent,
                    contentColor = if (selected) PrimaryPurple else MaterialTheme.colorScheme.onSurfaceVariant,
                ),
            ) {
                Text(label, fontWeight = if (selected) FontWeight.Medium else FontWeight.Normal)
                if (page == 2 && unreadCount > 0) {
                    Box(
                        modifier = Modifier.padding(start = 6.dp).size(20.dp)
                            .background(PrimaryPurple, CircleShape),
                        contentAlignment = Alignment.Center,
                    ) {
                        Text(
                            text = unreadCount.coerceAtMost(99).toString(),
                            color = Color.White,
                            fontSize = 11.sp,
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun SettingsScreen(
    accountEmail: String?,
    token: String?,
    profileName: String,
    sunSign: String?,
    moonSign: String?,
    ascendantSign: String?,
    onEditProfile: () -> Unit,
    onAbout: () -> Unit,
    onLogout: () -> Unit,
    onAccountDeleted: () -> Unit,
    betaPremiumEnabled: Boolean,
    onBetaPremiumChange: (Boolean) -> Unit,
    onBack: () -> Unit,
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    var myProfile by remember { mutableStateOf<SocialUser?>(null) }
    var statusUpdating by remember { mutableStateOf(false) }
    var showAiInfo by remember { mutableStateOf(false) }
    var showDeleteConfirmation by remember { mutableStateOf(false) }
    var deletingAccount by remember { mutableStateOf(false) }
    var settingsMessage by remember { mutableStateOf<String?>(null) }
    var settingsMessageIsError by remember { mutableStateOf(false) }
    val statusOptions = listOf(
        "Gökyüzünü dinliyor ✦",
        "Bugün biraz sessiz ☾",
        "Yeni başlangıçlara açık",
        "Kendime zaman ayırıyorum",
    )
    LaunchedEffect(token) {
        myProfile = token?.let { runCatching { fetchSocialOverview(it).me }.getOrNull() }
    }
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState())
            .padding(horizontal = 22.dp),
    ) {
        TextButton(onClick = onBack) { Text("‹ Haritama dön") }
        Text("Ayarlar", style = MaterialTheme.typography.headlineMedium)
        Card(
            modifier = Modifier.fillMaxWidth().padding(top = 8.dp, bottom = 18.dp),
            colors = CardDefaults.cardColors(containerColor = SoftSurface),
            shape = RoundedCornerShape(22.dp),
        ) {
            Column(Modifier.padding(18.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        Modifier.size(54.dp).background(Color.White.copy(alpha = 0.14f), CircleShape),
                        contentAlignment = Alignment.Center,
                    ) {
                        Text(profileName.take(1).uppercase(), color = Color.White, fontSize = 21.sp, fontWeight = FontWeight.Bold)
                    }
                    Column(Modifier.padding(start = 13.dp)) {
                        Text(profileName, color = Color.White, fontSize = 19.sp, fontWeight = FontWeight.SemiBold)
                        Text(accountEmail.orEmpty(), color = Color.White.copy(alpha = 0.68f), style = MaterialTheme.typography.bodySmall)
                        myProfile?.olimoraId?.let { olimoraId ->
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text(
                                    olimoraId,
                                    color = Gold,
                                    modifier = Modifier.weight(1f, fill = false).padding(top = 2.dp),
                                    style = MaterialTheme.typography.bodySmall,
                                )
                                TextButton(
                                    onClick = {
                                        val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                                        clipboard.setPrimaryClip(ClipData.newPlainText("Olimora arkadaş kodu", olimoraId))
                                        settingsMessage = "Arkadaş kodun kopyalandı."
                                        settingsMessageIsError = false
                                    },
                                    contentPadding = PaddingValues(horizontal = 8.dp, vertical = 0.dp),
                                ) {
                                    Text("Kopyala", color = Gold, fontSize = 11.sp)
                                }
                            }
                        }
                    }
                }
                if (sunSign != null && moonSign != null && ascendantSign != null) {
                    Text(
                        "${signName(sunSign)} Güneş  ·  ${signName(moonSign)} Ay  ·  ${signName(ascendantSign)} Yükselen",
                        modifier = Modifier.padding(top = 14.dp),
                        color = Color.White.copy(alpha = 0.82f),
                        style = MaterialTheme.typography.bodySmall,
                    )
                }
            }
        }

        Text("Profil", fontWeight = FontWeight.SemiBold, fontSize = 18.sp, modifier = Modifier.padding(bottom = 9.dp))
        SelectionField(
            label = "Kısa durumun",
            value = myProfile?.statusMessage ?: "Bir durum seç",
            options = statusOptions,
            onSelected = { selected ->
                val currentToken = token ?: return@SelectionField
                statusUpdating = true
                coroutineScope.launch {
                    runCatching { updateSocialStatus(currentToken, selected) }
                        .onSuccess {
                            myProfile = myProfile?.copy(statusMessage = selected)
                            settingsMessage = "Durumun güncellendi."
                            settingsMessageIsError = false
                        }
                        .onFailure {
                            settingsMessage = it.message ?: "Durum güncellenemedi."
                            settingsMessageIsError = true
                        }
                    statusUpdating = false
                }
            },
            modifier = Modifier.fillMaxWidth().padding(bottom = 10.dp),
        )
        if (statusUpdating) {
            Text("Durumun güncelleniyor…", color = MaterialTheme.colorScheme.onSurfaceVariant, style = MaterialTheme.typography.bodySmall)
        }
        settingsMessage?.let { message ->
            StatusNotice(
                message = message,
                isError = settingsMessageIsError,
                modifier = Modifier.padding(bottom = 10.dp),
            )
        }
        SettingsAction(
            title = "Doğum profilimi düzenle",
            description = "Doğum tarihi, saat ve yer bilgilerini güncelle",
            onClick = onEditProfile,
        )
        SettingsAction(
            title = "Bildirimler",
            description = "Yeni arkadaş mesajları için cihaz izinlerini yönet",
            onClick = {
                val intent = Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS).apply {
                    putExtra(Settings.EXTRA_APP_PACKAGE, context.packageName)
                }
                context.startActivity(intent)
            },
        )
        SettingsAction(
            title = if (betaPremiumEnabled) "Beta Premium · Açık" else "Beta Premium'u dene",
            description = if (betaPremiumEnabled) {
                "Kişisel Premium yorumları test edebilirsin; ücret alınmaz"
            } else {
                "Ödeme yapmadan Premium yorum akışını test için etkinleştir"
            },
            onClick = { onBetaPremiumChange(!betaPremiumEnabled) },
        )
        Text("Gizlilik ve güven", fontWeight = FontWeight.SemiBold, fontSize = 18.sp, modifier = Modifier.padding(top = 10.dp, bottom = 9.dp))
        SettingsAction(
            title = "AI nasıl kullanılıyor?",
            description = "Athena’nın hangi verileri yorumladığını açıkça gör",
            onClick = { showAiInfo = true },
        )
        SettingsAction(
            title = "Hakkında ve destek",
            description = "Açık kaynak, lisans, destek ve sürüm bilgileri",
            onClick = onAbout,
        )
        SettingsAction(
            title = "Hesabımı ve verilerimi sil",
            description = "Profilini, mesaj bağlantılarını ve kayıtlı haritanı kalıcı olarak kaldır",
            onClick = { showDeleteConfirmation = true },
        )
        OutlinedButton(
            onClick = onLogout,
            modifier = Modifier.fillMaxWidth().padding(top = 18.dp),
            shape = RoundedCornerShape(14.dp),
        ) { Text("Çıkış yap") }
    }

    if (showAiInfo) {
        AlertDialog(
            onDismissRequest = { showAiInfo = false },
            title = { Text("Athena ve verilerin") },
            text = {
                Text("Athena; doğum tarihi, saat, konum ve astroloji motorunun ürettiği matematiksel yerleşimleri yorumlar. Arkadaş mesajların ve paylaştığın fotoğraflar AI yorumuna gönderilmez.")
            },
            confirmButton = { TextButton(onClick = { showAiInfo = false }) { Text("Anladım") } },
            shape = RoundedCornerShape(22.dp),
        )
    }
    if (showDeleteConfirmation) {
        AlertDialog(
            onDismissRequest = { if (!deletingAccount) showDeleteConfirmation = false },
            title = { Text("Hesabın kalıcı olarak silinsin mi?") },
            text = { Text("Bu işlem geri alınamaz. Doğum profilin, haritan ve sosyal bağlantıların sunucudan kaldırılır.") },
            confirmButton = {
                Button(
                    enabled = !deletingAccount,
                    onClick = {
                        val currentToken = token ?: return@Button
                        deletingAccount = true
                        coroutineScope.launch {
                            runCatching { deleteAccount(currentToken) }
                                .onSuccess { onAccountDeleted() }
                                .onFailure {
                                    settingsMessage = it.message ?: "Hesap şu anda silinemedi. Lütfen tekrar dene."
                                    settingsMessageIsError = true
                                    deletingAccount = false
                                    showDeleteConfirmation = false
                                }
                        }
                    },
                ) { Text(if (deletingAccount) "Siliniyor…" else "Evet, kalıcı olarak sil") }
            },
            dismissButton = { TextButton(onClick = { showDeleteConfirmation = false }) { Text("Vazgeç") } },
            shape = RoundedCornerShape(22.dp),
        )
    }
}

@Composable
private fun StatusNotice(
    message: String,
    isError: Boolean,
    modifier: Modifier = Modifier,
    actionLabel: String? = null,
    onAction: (() -> Unit)? = null,
) {
    val accent = if (isError) MaterialTheme.colorScheme.error else Color(0xFF2E7D5B)
    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = accent.copy(alpha = 0.08f)),
        border = BorderStroke(1.dp, accent.copy(alpha = 0.28f)),
        shape = RoundedCornerShape(14.dp),
    ) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 13.dp, vertical = 11.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(if (isError) "!" else "✓", color = accent, fontWeight = FontWeight.Bold)
            Text(
                message,
                modifier = Modifier.weight(1f).padding(start = 9.dp),
                color = MaterialTheme.colorScheme.onSurface,
                style = MaterialTheme.typography.bodySmall,
            )
            if (actionLabel != null && onAction != null) {
                TextButton(onClick = onAction) { Text(actionLabel, color = accent) }
            }
        }
    }
}

@Composable
private fun SettingsAction(
    title: String,
    description: String,
    onClick: () -> Unit,
) {
    OutlinedButton(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth().padding(bottom = 10.dp),
        shape = RoundedCornerShape(16.dp),
        contentPadding = PaddingValues(16.dp),
    ) {
        Column(Modifier.weight(1f)) {
            Text(title, color = MaterialTheme.colorScheme.onSurface, fontWeight = FontWeight.Medium)
            Text(
                description,
                modifier = Modifier.padding(top = 3.dp),
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                style = MaterialTheme.typography.bodySmall,
            )
        }
        Text("›", color = PrimaryPurple, fontSize = 22.sp)
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun SocialScreen(
    token: String,
    onConversationChanged: (Boolean) -> Unit = {},
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    var overview by remember { mutableStateOf<SocialOverview?>(null) }
    var selectedFriend by remember { mutableStateOf<SocialUser?>(null) }
    var groups by remember { mutableStateOf<List<SocialGroup>>(emptyList()) }
    var selectedGroup by remember { mutableStateOf<SocialGroup?>(null) }
    var loading by remember { mutableStateOf(true) }
    var error by remember { mutableStateOf<String?>(null) }
    var refreshKey by remember { mutableStateOf(0) }

    fun closeConversation() {
        selectedFriend = null
        selectedGroup = null
        onConversationChanged(false)
    }

    BackHandler(enabled = selectedFriend != null || selectedGroup != null) {
        closeConversation()
    }

    LaunchedEffect(refreshKey) {
        loading = true
        error = null
        while (true) {
            try {
                overview = fetchSocialOverview(token)
                groups = fetchGroups(token)
                error = null
            } catch (exception: Exception) {
                error = exception.message ?: "Arkadaşlar yüklenemedi."
            } finally {
                loading = false
            }
            delay(30_000)
        }
    }

    selectedFriend?.let { friend ->
        ConversationScreen(
            token = token,
            friend = friend,
            onBack = { closeConversation() },
        )
        return
    }

    selectedGroup?.let { group ->
        GroupConversationScreen(
            token = token,
            group = group,
            currentUserId = overview?.me?.id.orEmpty(),
            onBack = { closeConversation() },
            onLeft = {
                closeConversation()
                refreshKey += 1
            },
        )
        return
    }

    var friendOlimoraId by remember { mutableStateOf("") }
    var actionLoading by remember { mutableStateOf(false) }
    var showAddFriend by remember { mutableStateOf(false) }
    var showCreateGroup by remember { mutableStateOf(false) }
    var groupName by remember { mutableStateOf("") }
    var selectedGroupMembers by remember { mutableStateOf<Set<String>>(emptySet()) }
    PullToRefreshBox(
        isRefreshing = loading,
        onRefresh = { refreshKey += 1 },
        modifier = Modifier.fillMaxSize(),
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 22.dp),
        ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                text = "Arkadaşların",
                modifier = Modifier.weight(1f),
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Medium,
            )
            TextButton(onClick = { showAddFriend = true }) {
                Text("＋ Arkadaş ekle")
            }
        }
        Text(
            text = "Athena ekranına dönmek için sağa kaydır.",
            modifier = Modifier.padding(top = 6.dp, bottom = 18.dp),
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        error?.let { message ->
            StatusNotice(
                message = message,
                isError = true,
                modifier = Modifier.padding(top = 10.dp),
                actionLabel = "Tekrar dene",
                onAction = { refreshKey += 1 },
            )
        }
        if (loading) {
            Text(
                "Arkadaşların yükleniyor…",
                modifier = Modifier.padding(top = 22.dp),
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }

        overview?.incoming?.takeIf { it.isNotEmpty() }?.let { requests ->
            SocialSectionTitle("Gelen istekler")
            requests.forEach { request ->
                FriendRequestCard(
                    name = request.user.displayName,
                    olimoraId = request.user.olimoraId,
                    onAccept = {
                        coroutineScope.launch {
                            runCatching { acceptFriendRequest(token, request.id) }
                                .onFailure { error = it.message }
                            refreshKey += 1
                        }
                    },
                    onDecline = {
                        coroutineScope.launch {
                            runCatching { declineFriendRequest(token, request.id) }
                                .onFailure { error = it.message }
                            refreshKey += 1
                        }
                    },
                )
            }
        }

        Row(
            modifier = Modifier.fillMaxWidth().padding(top = 18.dp, bottom = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text("Gruplar", modifier = Modifier.weight(1f), fontWeight = FontWeight.SemiBold, fontSize = 18.sp)
            TextButton(onClick = { showCreateGroup = true }) { Text("＋ Grup kur") }
        }
        if (!loading && groups.isEmpty()) {
            Text(
                "Henüz grubun yok. Arkadaşlarınla ilk Olimora grubunu kurabilirsin.",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                style = MaterialTheme.typography.bodySmall,
            )
        }
        groups.forEach { group ->
            GroupRow(
                group = group,
                onClick = {
                    selectedGroup = group
                    onConversationChanged(true)
                },
            )
        }

        SocialSectionTitle("Özel sohbetler")
        val friends = overview?.friends.orEmpty()
        if (!loading && friends.isEmpty()) {
            Text(
                "Henüz arkadaşın yok. Olimora ID ile ilk isteğini gönderebilirsin.",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        friends.forEach { friend ->
            FriendRow(
                friend = friend,
                onClick = {
                    selectedFriend = friend
                    onConversationChanged(true)
                },
            )
        }

        overview?.outgoing?.takeIf { it.isNotEmpty() }?.let { requests ->
            SocialSectionTitle("Gönderilen istekler")
            requests.forEach { request ->
                Card(
                    modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                    border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline),
                    shape = RoundedCornerShape(14.dp),
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth().padding(14.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Column(Modifier.weight(1f)) {
                            Text(request.user.displayName, fontWeight = FontWeight.Medium)
                            Text(
                                "Yanıt bekleniyor",
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                                style = MaterialTheme.typography.bodySmall,
                            )
                        }
                        TextButton(onClick = {
                            coroutineScope.launch {
                                runCatching { declineFriendRequest(token, request.id) }
                                refreshKey += 1
                            }
                        }) { Text("İptal") }
                    }
                }
            }
        }
            Spacer(Modifier.height(28.dp))
        }
    }

    if (showAddFriend) {
        AlertDialog(
            onDismissRequest = { if (!actionLoading) showAddFriend = false },
            title = { Text("Arkadaş ekle") },
            text = {
                Column {
                    OutlinedTextField(
                        value = friendOlimoraId,
                        onValueChange = { friendOlimoraId = normalizeFriendCode(it) },
                        label = { Text("Arkadaşının Olimora ID'si") },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth(),
                    )
                    TextButton(
                        onClick = {
                            val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                            val pasted = clipboard.primaryClip
                                ?.getItemAt(0)
                                ?.coerceToText(context)
                                ?.toString()
                                .orEmpty()
                            friendOlimoraId = normalizeFriendCode(pasted)
                        },
                        modifier = Modifier.align(Alignment.End),
                    ) {
                        Text("Panodan yapıştır")
                    }
                }
            },
            confirmButton = {
                Button(
                    enabled = !actionLoading && friendOlimoraId.isNotBlank(),
                    onClick = {
                        actionLoading = true
                        error = null
                        coroutineScope.launch {
                            try {
                                sendFriendRequest(token, friendOlimoraId)
                                friendOlimoraId = ""
                                showAddFriend = false
                                refreshKey += 1
                            } catch (exception: Exception) {
                                error = exception.message ?: "İstek gönderilemedi."
                            } finally {
                                actionLoading = false
                            }
                        }
                    },
                ) { Text(if (actionLoading) "Gönderiliyor…" else "İstek gönder") }
            },
            dismissButton = {
                TextButton(
                    enabled = !actionLoading,
                    onClick = { showAddFriend = false },
                ) { Text("Vazgeç") }
            },
            shape = RoundedCornerShape(22.dp),
        )
    }

    if (showCreateGroup) {
        AlertDialog(
            onDismissRequest = { if (!actionLoading) showCreateGroup = false },
            title = { Text("Yeni grup") },
            text = {
                Column(Modifier.verticalScroll(rememberScrollState())) {
                    OutlinedTextField(
                        value = groupName,
                        onValueChange = { groupName = it.take(60) },
                        label = { Text("Grup adı") },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth(),
                    )
                    Text(
                        "Davet edilecek arkadaşlar",
                        modifier = Modifier.padding(top = 16.dp, bottom = 6.dp),
                        fontWeight = FontWeight.Medium,
                    )
                    overview?.friends.orEmpty().forEach { friend ->
                        val selected = friend.id in selectedGroupMembers
                        TextButton(
                            onClick = {
                                selectedGroupMembers = if (selected) selectedGroupMembers - friend.id
                                else if (selectedGroupMembers.size < 19) {
                                    selectedGroupMembers + friend.id
                                } else {
                                    selectedGroupMembers
                                }
                            },
                            modifier = Modifier.fillMaxWidth(),
                        ) {
                            Text(if (selected) "✓" else "○", color = PrimaryPurple, fontSize = 18.sp)
                            Text(friend.displayName, modifier = Modifier.padding(start = 10.dp).weight(1f), textAlign = TextAlign.Start)
                        }
                    }
                    Text(
                        "${selectedGroupMembers.size}/19 kişi seçildi",
                        modifier = Modifier.padding(top = 8.dp),
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        style = MaterialTheme.typography.bodySmall,
                    )
                }
            },
            confirmButton = {
                Button(
                    enabled = !actionLoading && groupName.trim().length >= 2,
                    onClick = {
                        actionLoading = true
                        coroutineScope.launch {
                            try {
                                createGroup(token, groupName, selectedGroupMembers.toList())
                                groupName = ""
                                selectedGroupMembers = emptySet()
                                showCreateGroup = false
                                refreshKey += 1
                            } catch (exception: Exception) {
                                error = exception.message ?: "Grup oluşturulamadı."
                            } finally {
                                actionLoading = false
                            }
                        }
                    },
                ) { Text(if (actionLoading) "Kuruluyor…" else "Grubu kur") }
            },
            dismissButton = {
                TextButton(onClick = { showCreateGroup = false }) { Text("Vazgeç") }
            },
            shape = RoundedCornerShape(22.dp),
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun ConversationScreen(
    token: String,
    friend: SocialUser,
    onBack: () -> Unit,
    previewMessages: List<DirectMessage>? = null,
) {
    val coroutineScope = rememberCoroutineScope()
    var messages by remember(friend.id) { mutableStateOf(previewMessages.orEmpty()) }
    var draft by remember(friend.id) { mutableStateOf("") }
    var loading by remember(friend.id) { mutableStateOf(true) }
    var error by remember(friend.id) { mutableStateOf<String?>(null) }
    var refreshKey by remember(friend.id) { mutableStateOf(0) }
    var sending by remember(friend.id) { mutableStateOf(false) }
    val messageListState = rememberLazyListState()
    var liveFriend by remember(friend.id) { mutableStateOf(friend) }

    LaunchedEffect(friend.id) {
        if (previewMessages != null) return@LaunchedEffect
        while (true) {
            runCatching { fetchSocialOverview(token) }
                .getOrNull()
                ?.friends
                ?.firstOrNull { it.id == friend.id }
                ?.let { liveFriend = it }
            delay(20_000)
        }
    }

    LaunchedEffect(friend.id, refreshKey) {
        if (previewMessages != null) {
            loading = false
            return@LaunchedEffect
        }
        loading = true
        while (true) {
            try {
                messages = fetchMessages(token, friend.id)
                error = null
            } catch (exception: Exception) {
                error = exception.message ?: "Mesajlar yüklenemedi."
            } finally {
                loading = false
            }
            delay(4_000)
        }
    }

    LaunchedEffect(messages.lastOrNull()?.id, sending) {
        if (messages.isNotEmpty()) {
            delay(60)
            val lastItem = messageListState.layoutInfo.totalItemsCount - 1
            if (lastItem >= 0) messageListState.animateScrollToItem(lastItem)
        }
    }

    val conversationBackground = Brush.verticalGradient(
        listOf(
            PrimaryPurple.copy(alpha = 0.10f),
            MaterialTheme.colorScheme.background,
            MaterialTheme.colorScheme.background,
        )
    )
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(conversationBackground)
            .padding(horizontal = 14.dp),
    ) {
        Card(
            modifier = Modifier.fillMaxWidth().padding(top = 6.dp, bottom = 10.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
            border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline.copy(alpha = 0.7f)),
            shape = RoundedCornerShape(22.dp),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 8.dp, vertical = 7.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                TextButton(onClick = onBack, contentPadding = PaddingValues(horizontal = 8.dp)) {
                    Text("‹", color = PrimaryPurple, fontSize = 30.sp)
                }
                Box(
                    modifier = Modifier
                        .size(44.dp)
                        .background(PrimaryPurple.copy(alpha = 0.14f), CircleShape),
                    contentAlignment = Alignment.Center,
                ) {
                    Text(
                        liveFriend.displayName.take(1).uppercase(),
                        color = PrimaryPurple,
                        fontWeight = FontWeight.SemiBold,
                        fontSize = 18.sp,
                    )
                }
                Column(Modifier.weight(1f).padding(start = 11.dp)) {
                    Text(liveFriend.displayName, fontWeight = FontWeight.SemiBold, fontSize = 17.sp)
                    Text(
                        formatPresence(liveFriend),
                        color = if (liveFriend.isOnline) Color(0xFF2E9B62)
                        else MaterialTheme.colorScheme.onSurfaceVariant,
                        style = MaterialTheme.typography.bodySmall,
                    )
                }
            }
        }
        PullToRefreshBox(
            isRefreshing = loading,
            onRefresh = { refreshKey += 1 },
            modifier = Modifier.weight(1f),
        ) {
            LazyColumn(
                state = messageListState,
                modifier = Modifier.fillMaxSize(),
                verticalArrangement = Arrangement.Bottom,
            ) {
                item { CompatibilityPreviewCard(friendName = liveFriend.displayName) }
                if (loading && messages.isEmpty()) {
                    item {
                        Text("Mesajlar yükleniyor…", color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
                items(messages.size, key = { messages[it].id }) { index ->
                    MessageBubble(messages[index])
                }
                error?.let { message ->
                    item {
                        StatusNotice(
                            message = message,
                            isError = true,
                            modifier = Modifier.padding(vertical = 8.dp),
                        )
                    }
                }
                item { Spacer(Modifier.height(8.dp)) }
            }
        }
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .imePadding()
                .padding(vertical = 10.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
            border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline.copy(alpha = 0.65f)),
            shape = RoundedCornerShape(22.dp),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth().padding(8.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                OutlinedTextField(
                    value = draft,
                    onValueChange = { if (it.length <= 2000) draft = it },
                    placeholder = { Text("Mesaj yaz…") },
                    modifier = Modifier.weight(1f),
                    maxLines = 4,
                    shape = RoundedCornerShape(18.dp),
                )
                Spacer(Modifier.width(7.dp))
                Button(
                    onClick = {
                        val body = draft.trim()
                        if (body.isEmpty()) return@Button
                        sending = true
                        draft = ""
                        coroutineScope.launch {
                            try {
                                val sentMessage = sendDirectMessage(token, friend.id, body)
                                messages = messages + sentMessage
                                refreshKey += 1
                            } catch (exception: Exception) {
                                draft = body
                                error = exception.message
                            } finally {
                                sending = false
                            }
                        }
                    },
                    enabled = draft.isNotBlank() && !sending,
                    modifier = Modifier.size(50.dp),
                    contentPadding = PaddingValues(0.dp),
                    shape = CircleShape,
                    colors = ButtonDefaults.buttonColors(containerColor = PrimaryPurple),
                ) {
                    if (sending) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(20.dp),
                            color = Color.White,
                            strokeWidth = 2.dp,
                        )
                    } else {
                        Text("➤", fontSize = 19.sp)
                    }
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun GroupConversationScreen(
    token: String,
    group: SocialGroup,
    currentUserId: String,
    onBack: () -> Unit,
    onLeft: () -> Unit,
) {
    val coroutineScope = rememberCoroutineScope()
    var messages by remember(group.id) { mutableStateOf<List<GroupMessage>>(emptyList()) }
    var draft by remember(group.id) { mutableStateOf("") }
    var loading by remember(group.id) { mutableStateOf(true) }
    var sending by remember(group.id) { mutableStateOf(false) }
    var error by remember(group.id) { mutableStateOf<String?>(null) }
    var refreshKey by remember(group.id) { mutableStateOf(0) }
    var showInfo by remember(group.id) { mutableStateOf(false) }
    val listState = rememberLazyListState()

    LaunchedEffect(group.id, refreshKey) {
        while (true) {
            try {
                messages = fetchGroupMessages(token, group.id)
                error = null
            } catch (exception: Exception) {
                error = exception.message ?: "Grup mesajları yüklenemedi."
            } finally {
                loading = false
            }
            delay(4_000)
        }
    }
    LaunchedEffect(messages.size, draft) {
        if (messages.isNotEmpty()) listState.scrollToItem(messages.lastIndex)
    }

    Column(
        modifier = Modifier.fillMaxSize().background(
            Brush.verticalGradient(
                listOf(PrimaryPurple.copy(alpha = 0.10f), MaterialTheme.colorScheme.background)
            )
        ).padding(horizontal = 14.dp),
    ) {
        Card(
            modifier = Modifier.fillMaxWidth().padding(top = 6.dp, bottom = 10.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
            border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline.copy(alpha = 0.7f)),
            shape = RoundedCornerShape(22.dp),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 8.dp, vertical = 7.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                TextButton(onClick = onBack, contentPadding = PaddingValues(horizontal = 8.dp)) {
                    Text("‹", color = PrimaryPurple, fontSize = 30.sp)
                }
                Box(
                    Modifier.size(44.dp).background(PrimaryPurple.copy(alpha = 0.14f), CircleShape),
                    contentAlignment = Alignment.Center,
                ) { Text("✦", color = Gold, fontSize = 20.sp) }
                Column(Modifier.weight(1f).padding(start = 11.dp)) {
                    Text(group.name, fontWeight = FontWeight.SemiBold, fontSize = 17.sp)
                    Text("${group.members.size} üye", color = MaterialTheme.colorScheme.onSurfaceVariant, style = MaterialTheme.typography.bodySmall)
                }
                TextButton(onClick = { showInfo = true }) { Text("Üyeler") }
            }
        }
        PullToRefreshBox(
            isRefreshing = loading,
            onRefresh = { refreshKey += 1 },
            modifier = Modifier.weight(1f),
        ) {
            LazyColumn(state = listState, modifier = Modifier.fillMaxSize(), verticalArrangement = Arrangement.Bottom) {
                if (loading && messages.isEmpty()) {
                    item { Text("Grup hazırlanıyor…", color = MaterialTheme.colorScheme.onSurfaceVariant) }
                }
                items(messages.size, key = { messages[it].id }) { index ->
                    GroupMessageBubble(messages[index])
                }
                error?.let { message -> item { StatusNotice(message, true, Modifier.padding(vertical = 8.dp)) } }
                item { Spacer(Modifier.height(8.dp)) }
            }
        }
        Card(
            modifier = Modifier.fillMaxWidth().imePadding().padding(vertical = 10.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
            border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline.copy(alpha = 0.65f)),
            shape = RoundedCornerShape(22.dp),
        ) {
            Row(
                Modifier.fillMaxWidth().padding(8.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                OutlinedTextField(
                    value = draft,
                    onValueChange = { if (it.length <= 2000) draft = it },
                    placeholder = { Text("Gruba yaz…") },
                    modifier = Modifier.weight(1f),
                    maxLines = 4,
                    shape = RoundedCornerShape(18.dp),
                )
                Spacer(Modifier.width(7.dp))
                Button(
                    onClick = {
                        val body = draft.trim()
                        if (body.isEmpty()) return@Button
                        sending = true
                        draft = ""
                        coroutineScope.launch {
                            try {
                                sendGroupMessage(token, group.id, body)
                                refreshKey += 1
                            } catch (exception: Exception) {
                                draft = body
                                error = exception.message
                            } finally {
                                sending = false
                            }
                        }
                    },
                    enabled = draft.isNotBlank() && !sending,
                    modifier = Modifier.size(50.dp),
                    contentPadding = PaddingValues(0.dp),
                    shape = CircleShape,
                ) { Text(if (sending) "…" else "➤", fontSize = 19.sp) }
            }
        }
    }

    if (showInfo) {
        AlertDialog(
            onDismissRequest = { showInfo = false },
            title = { Text(group.name) },
            text = {
                Column {
                    group.members.forEach { member ->
                        Row(Modifier.fillMaxWidth().padding(vertical = 7.dp)) {
                            Text(member.user.displayName, modifier = Modifier.weight(1f))
                            if (member.role == "owner") Text("Kurucu", color = Gold, fontSize = 12.sp)
                        }
                    }
                    TextButton(
                        onClick = {
                            coroutineScope.launch {
                                runCatching { leaveGroup(token, group.id) }
                                    .onSuccess { onLeft() }
                                    .onFailure { error = it.message }
                            }
                        },
                        modifier = Modifier.fillMaxWidth().padding(top = 12.dp),
                    ) {
                        Text(
                            if (group.ownerId == currentUserId) "Grubu sil" else "Gruptan ayrıl",
                            color = Color(0xFFC44747),
                        )
                    }
                }
            },
            confirmButton = { TextButton(onClick = { showInfo = false }) { Text("Kapat") } },
        )
    }
}

@Composable
private fun GroupMessageBubble(message: GroupMessage) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(vertical = 3.dp),
        horizontalArrangement = if (message.isMine) Arrangement.End else Arrangement.Start,
    ) {
        Card(
            modifier = Modifier.widthIn(max = 286.dp),
            colors = CardDefaults.cardColors(
                containerColor = if (message.isMine) PrimaryPurple else MaterialTheme.colorScheme.surface
            ),
            border = if (message.isMine) null else BorderStroke(1.dp, MaterialTheme.colorScheme.outline),
            shape = RoundedCornerShape(18.dp),
        ) {
            Column(Modifier.padding(horizontal = 13.dp, vertical = 9.dp)) {
                if (!message.isMine) Text(message.sender.displayName, color = PrimaryPurple, fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
                Text(message.body, color = if (message.isMine) Color.White else MaterialTheme.colorScheme.onSurface)
                Text(
                    formatMessageTime(message.createdAt),
                    modifier = Modifier.align(Alignment.End).padding(top = 3.dp),
                    color = if (message.isMine) Color.White.copy(alpha = 0.72f) else MaterialTheme.colorScheme.onSurfaceVariant,
                    fontSize = 10.sp,
                )
            }
        }
    }
}

@Composable
private fun CompatibilityPreviewCard(friendName: String) {
    Card(
        modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
        colors = CardDefaults.cardColors(containerColor = PrimaryPurple.copy(alpha = 0.08f)),
        border = BorderStroke(1.dp, Gold.copy(alpha = 0.45f)),
        shape = RoundedCornerShape(18.dp),
    ) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(14.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text("✦", color = Gold, fontSize = 22.sp)
            Column(Modifier.weight(1f).padding(horizontal = 11.dp)) {
                Text("$friendName ile haritalarınızı karşılaştır", fontWeight = FontWeight.Medium)
                Text(
                    "İletişim, duygu ve ortak enerji başlıkları",
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    style = MaterialTheme.typography.bodySmall,
                )
            }
            Text("Premium", color = Color(0xFF9A6812), fontSize = 11.sp, fontWeight = FontWeight.Bold)
        }
    }
}

@Composable
private fun MessageBubble(message: DirectMessage) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(vertical = 3.dp),
        horizontalArrangement = if (message.isMine) Arrangement.End else Arrangement.Start,
    ) {
        Card(
            modifier = Modifier.widthIn(max = 286.dp),
            colors = CardDefaults.cardColors(
                containerColor = if (message.isMine) PrimaryPurple else MaterialTheme.colorScheme.surface
            ),
            border = if (message.isMine) null else BorderStroke(1.dp, MaterialTheme.colorScheme.outline),
            shape = if (message.isMine) {
                RoundedCornerShape(
                    topStart = 18.dp,
                    topEnd = 18.dp,
                    bottomStart = 18.dp,
                    bottomEnd = 5.dp,
                )
            } else {
                RoundedCornerShape(
                    topStart = 18.dp,
                    topEnd = 18.dp,
                    bottomStart = 5.dp,
                    bottomEnd = 18.dp,
                )
            },
        ) {
            Column(Modifier.padding(horizontal = 13.dp, vertical = 9.dp)) {
                Text(
                    message.body,
                    color = if (message.isMine) Color.White else MaterialTheme.colorScheme.onSurface,
                )
                Row(
                    modifier = Modifier.align(Alignment.End).padding(top = 3.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text(
                        formatMessageTime(message.createdAt),
                        color = if (message.isMine) Color.White.copy(alpha = 0.72f)
                        else MaterialTheme.colorScheme.onSurfaceVariant,
                        fontSize = 10.sp,
                    )
                    if (message.isMine) {
                        Text(
                            text = "✦",
                            modifier = Modifier.padding(start = 5.dp),
                            color = if (message.readAt != null) Gold
                            else Color.White.copy(alpha = 0.42f),
                            fontSize = 12.sp,
                            fontWeight = if (message.readAt != null) FontWeight.Bold
                            else FontWeight.Normal,
                        )
                    }
                }
            }
        }
    }
}

private fun formatMessageTime(value: String): String {
    val normalized = value.replace(
        Regex("\\.(\\d{3})\\d*(Z|[+-]\\d{2}:\\d{2})$"),
        ".$1$2",
    )
    val inputPatterns = listOf(
        "yyyy-MM-dd'T'HH:mm:ss.SSSX",
        "yyyy-MM-dd'T'HH:mm:ssX",
    )
    val parsed = inputPatterns.firstNotNullOfOrNull { pattern ->
        runCatching {
            SimpleDateFormat(pattern, Locale.US).apply {
                isLenient = false
                timeZone = java.util.TimeZone.getTimeZone("UTC")
            }.parse(normalized)
        }.getOrNull()
    } ?: return Regex("T(\\d{2}:\\d{2})").find(value)?.groupValues?.get(1) ?: ""
    return SimpleDateFormat("HH:mm", Locale.getDefault()).format(parsed)
}

private fun normalizeFriendCode(value: String): String = value
    .trim()
    .substringAfterLast('/')
    .removePrefix("@")
    .lowercase()
    .filter { it.isLetterOrDigit() || it == '_' }
    .take(21)

private fun formatPresence(friend: SocialUser): String {
    if (friend.isOnline) return "● Çevrimiçi · Olimora'da"
    val value = friend.lastSeenAt ?: return "Henüz aktiflik bilgisi yok"
    val normalized = value.replace(
        Regex("\\.(\\d{3})\\d*(Z|[+-]\\d{2}:\\d{2})$"),
        ".$1$2",
    )
    val parsed = listOf("yyyy-MM-dd'T'HH:mm:ss.SSSX", "yyyy-MM-dd'T'HH:mm:ssX")
        .firstNotNullOfOrNull { pattern ->
            runCatching {
                SimpleDateFormat(pattern, Locale.US).apply {
                    isLenient = false
                    timeZone = java.util.TimeZone.getTimeZone("UTC")
                }.parse(normalized)
            }.getOrNull()
        } ?: return "Son görülme bilinmiyor"
    val minutes = ((System.currentTimeMillis() - parsed.time).coerceAtLeast(0) / 60_000).toInt()
    return when {
        minutes < 1 -> "Az önce görüldü"
        minutes < 60 -> "Son görülme ${minutes} dk önce"
        minutes < 24 * 60 -> "Son görülme ${minutes / 60} sa önce"
        else -> "Son görülme " + SimpleDateFormat("dd.MM · HH:mm", Locale.getDefault()).format(parsed)
    }
}

@Composable
private fun SocialSectionTitle(text: String) {
    Text(
        text,
        modifier = Modifier.padding(top = 22.dp, bottom = 10.dp),
        fontWeight = FontWeight.Medium,
        fontSize = 18.sp,
    )
}

@Composable
private fun GroupRow(group: SocialGroup, onClick: () -> Unit) {
    OutlinedButton(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp),
        shape = RoundedCornerShape(16.dp),
        contentPadding = PaddingValues(14.dp),
    ) {
        Box(
            modifier = Modifier.size(44.dp).background(PrimaryPurple.copy(alpha = 0.12f), CircleShape),
            contentAlignment = Alignment.Center,
        ) { Text("✦", color = Gold, fontSize = 20.sp) }
        Column(Modifier.weight(1f).padding(start = 12.dp)) {
            Text(group.name, color = MaterialTheme.colorScheme.onSurface, fontWeight = FontWeight.Medium)
            Text(
                "${group.members.size} üye · Grup sohbeti",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                style = MaterialTheme.typography.bodySmall,
            )
        }
        if (group.unreadCount > 0) {
            Box(Modifier.size(24.dp).background(PrimaryPurple, CircleShape), contentAlignment = Alignment.Center) {
                Text(group.unreadCount.coerceAtMost(99).toString(), color = Color.White, fontSize = 11.sp)
            }
        } else {
            Text("›", color = PrimaryPurple, fontSize = 22.sp)
        }
    }
}

@Composable
private fun FriendRow(friend: SocialUser, onClick: () -> Unit) {
    OutlinedButton(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp),
        shape = RoundedCornerShape(14.dp),
        contentPadding = PaddingValues(14.dp),
    ) {
        Box(
            modifier = Modifier.size(42.dp).background(SoftSurface, CircleShape),
            contentAlignment = Alignment.Center,
        ) { Text(friend.displayName.take(1).uppercase(), color = Gold) }
        Column(Modifier.weight(1f).padding(start = 12.dp)) {
            Text(friend.displayName, color = MaterialTheme.colorScheme.onSurface)
            friend.statusMessage?.let { status ->
                Text(
                    status,
                    color = PrimaryPurple,
                    style = MaterialTheme.typography.bodySmall,
                )
            }
            Text(
                formatPresence(friend),
                color = if (friend.isOnline) Color(0xFF2E9B62)
                else MaterialTheme.colorScheme.onSurfaceVariant,
                fontSize = 10.sp,
            )
        }
        Text("Sohbet ›", color = PrimaryPurple)
    }
}

@Composable
private fun FriendRequestCard(
    name: String,
    olimoraId: String,
    onAccept: () -> Unit,
    onDecline: () -> Unit,
) {
    Card(
        modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline),
        shape = RoundedCornerShape(14.dp),
    ) {
        Column(Modifier.padding(14.dp)) {
            Text(name, fontWeight = FontWeight.Medium)
            Text(olimoraId, color = MaterialTheme.colorScheme.onSurfaceVariant)
            Row(Modifier.fillMaxWidth().padding(top = 8.dp), horizontalArrangement = Arrangement.End) {
                TextButton(onClick = onDecline) { Text("Reddet") }
                Button(
                    onClick = onAccept,
                    colors = ButtonDefaults.buttonColors(containerColor = PrimaryPurple),
                ) { Text("Kabul et") }
            }
        }
    }
}

@Composable
private fun AboutScreen(onBack: () -> Unit) {
    val context = LocalContext.current
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 22.dp),
    ) {
        Text("Olimora hakkında", style = MaterialTheme.typography.headlineMedium)
        Text(
            "Olimora, doğum haritasını anlaşılır ve kişisel bir deneyime dönüştüren bağımsız bir beta projesidir.",
            modifier = Modifier.padding(top = 10.dp, bottom = 20.dp),
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        AboutLink(
            label = "Destek ve geri bildirim",
            description = "Bir sorun bildir veya geliştirme önerini paylaş.",
            onClick = {
                context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("https://github.com/salihguduk680-code/olimora/issues")))
            },
        )
        Spacer(Modifier.height(10.dp))
        AboutLink(
            label = "Açık kaynak kodu",
            description = "Kaynak kodunu ve AGPL-3.0 lisansını görüntüle.",
            onClick = {
                context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("https://github.com/salihguduk680-code/olimora")))
            },
        )
        Text(
            "Astrolojik yorumlar eğlence ve öz farkındalık amaçlıdır.",
            modifier = Modifier.padding(top = 20.dp),
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        OutlinedButton(
            onClick = onBack,
            modifier = Modifier.fillMaxWidth().padding(top = 24.dp).height(52.dp),
            shape = RoundedCornerShape(14.dp),
        ) {
            Text("Geri dön")
        }
    }
}

@Composable
private fun AboutLink(label: String, description: String, onClick: () -> Unit) {
    OutlinedButton(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(14.dp),
        contentPadding = PaddingValues(16.dp),
    ) {
        Column(modifier = Modifier.fillMaxWidth()) {
            Text(label, fontWeight = FontWeight.Medium, color = MaterialTheme.colorScheme.onSurface)
            Text(
                description,
                modifier = Modifier.padding(top = 3.dp),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
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
private fun ChartWheelScreen(chart: BigThreeResult) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 18.dp, vertical = 10.dp),
    ) {
        Text(
            "Gökyüzü haritan",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.SemiBold,
        )
        Text(
            "Doğduğun andaki gezegenler, evler ve aralarındaki açılar.",
            modifier = Modifier.padding(top = 4.dp, bottom = 14.dp),
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        NatalChartWheel(chart)
        Text(
            "Harita özeti",
            modifier = Modifier.padding(top = 20.dp, bottom = 10.dp),
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.SemiBold,
        )
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            BigThreeCard(signSymbol(chart.sunSign), "Güneş", signName(chart.sunSign), chart.sunDegree, Modifier.weight(1f))
            BigThreeCard(signSymbol(chart.moonSign), "Ay", signName(chart.moonSign), chart.moonDegree, Modifier.weight(1f))
            BigThreeCard(signSymbol(chart.ascendantSign), "Yükselen", signName(chart.ascendantSign), chart.ascendantDegree, Modifier.weight(1f))
        }
        Text(
            "Açıların",
            modifier = Modifier.padding(top = 20.dp, bottom = 10.dp),
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.SemiBold,
        )
        DetailGroup(title = "Önemli açılar · ${chart.aspects.size}") {
            if (chart.aspects.isEmpty()) {
                Text(
                    "Seçili toleransa giren önemli bir açı bulunmadı.",
                    modifier = Modifier.padding(14.dp),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            } else {
                chart.aspects.take(8).forEachIndexed { index, aspect ->
                    AspectDetailRow(aspect)
                    if (index != minOf(7, chart.aspects.lastIndex)) DetailSeparator()
                }
                if (chart.aspects.size > 8) {
                    Text(
                        "+ ${chart.aspects.size - 8} açı daha · Tümünü Athena sayfasındaki detaylarda görebilirsin.",
                        modifier = Modifier.padding(14.dp),
                        color = PrimaryPurple,
                        style = MaterialTheme.typography.bodySmall,
                    )
                }
            }
        }
        Spacer(Modifier.height(28.dp))
    }
}

@Composable
private fun NatalChartWheel(chart: BigThreeResult) {
    var selectedPoint by remember { mutableStateOf<ChartPointResult?>(null) }
    val surfaceColor = MaterialTheme.colorScheme.surface
    val outlineColor = MaterialTheme.colorScheme.outline
    val textColor = MaterialTheme.colorScheme.onSurface
    val subtleTextColor = MaterialTheme.colorScheme.onSurfaceVariant
    val ascendantLongitude = chart.houses.firstOrNull { it.number == 1 }
        ?.let { zodiacLongitude(it.sign, it.degreeInSign) }
        ?: chart.positions.firstOrNull { it.name == "ascendant" }?.longitude
        ?: 0.0

    Card(
        colors = CardDefaults.cardColors(containerColor = surfaceColor),
        border = BorderStroke(1.dp, outlineColor),
        shape = RoundedCornerShape(18.dp),
    ) {
        Column(Modifier.padding(14.dp)) {
            Text("Doğum haritası çarkı", color = PrimaryPurple, fontWeight = FontWeight.SemiBold)
            Text(
                "Gezegen sembolüne dokunarak yerleşimini inceleyebilirsin.",
                modifier = Modifier.padding(top = 3.dp, bottom = 10.dp),
                color = subtleTextColor,
                style = MaterialTheme.typography.bodySmall,
            )
            Canvas(
                modifier = Modifier
                    .fillMaxWidth()
                    .aspectRatio(1f)
                    .pointerInput(chart, ascendantLongitude) {
                        detectTapGestures { tap ->
                            val center = Offset(size.width / 2f, size.height / 2f)
                            val radius = min(size.width, size.height) * 0.43f
                            selectedPoint = chart.positions
                                .map { it to wheelPoint(center, radius * 0.74f, it.longitude, ascendantLongitude) }
                                .minByOrNull { (_, point) -> distance(tap, point) }
                                ?.takeIf { (_, point) -> distance(tap, point) <= 32.dp.toPx() }
                                ?.first
                        }
                    },
            ) {
                val center = Offset(size.width / 2f, size.height / 2f)
                val radius = min(size.width, size.height) * 0.46f
                val zodiacInner = radius * 0.78f
                val houseInner = radius * 0.55f
                val aspectRadius = radius * 0.50f
                val textPaint = android.graphics.Paint().apply {
                    isAntiAlias = true
                    textAlign = android.graphics.Paint.Align.CENTER
                    typeface = android.graphics.Typeface.create(android.graphics.Typeface.DEFAULT, android.graphics.Typeface.BOLD)
                }

                drawCircle(Gold.copy(alpha = 0.10f), radius, center)
                drawCircle(outlineColor.copy(alpha = 0.65f), radius, center, style = Stroke(1.5.dp.toPx()))
                drawCircle(outlineColor.copy(alpha = 0.45f), zodiacInner, center, style = Stroke(1.dp.toPx()))
                drawCircle(outlineColor.copy(alpha = 0.35f), houseInner, center, style = Stroke(1.dp.toPx()))

                repeat(12) { index ->
                    val longitude = index * 30.0
                    val outer = wheelPoint(center, radius, longitude, ascendantLongitude)
                    val inner = wheelPoint(center, zodiacInner, longitude, ascendantLongitude)
                    drawLine(outlineColor.copy(alpha = 0.50f), inner, outer, 1.dp.toPx())
                    val labelPoint = wheelPoint(center, radius * 0.885f, longitude + 15.0, ascendantLongitude)
                    textPaint.color = zodiacColor(index).toArgb()
                    textPaint.textSize = 17.sp.toPx()
                    drawContext.canvas.nativeCanvas.drawText(
                        zodiacSymbols[index], labelPoint.x, labelPoint.y + textPaint.textSize * 0.34f, textPaint,
                    )
                }

                chart.houses.forEach { house ->
                    val longitude = zodiacLongitude(house.sign, house.degreeInSign)
                    val edge = wheelPoint(center, zodiacInner, longitude, ascendantLongitude)
                    val inner = wheelPoint(center, houseInner, longitude, ascendantLongitude)
                    drawLine(
                        if (house.number == 1 || house.number == 10) Gold else outlineColor,
                        inner,
                        edge,
                        if (house.number == 1 || house.number == 10) 2.dp.toPx() else 1.dp.toPx(),
                    )
                    val next = chart.houses.firstOrNull { it.number == house.number % 12 + 1 }
                    val nextLongitude = next?.let { zodiacLongitude(it.sign, it.degreeInSign) } ?: longitude + 30.0
                    val midpoint = circularMidpoint(longitude, nextLongitude)
                    val numberPoint = wheelPoint(center, radius * 0.655f, midpoint, ascendantLongitude)
                    textPaint.color = subtleTextColor.toArgb()
                    textPaint.textSize = 10.sp.toPx()
                    drawContext.canvas.nativeCanvas.drawText(
                        house.number.toString(), numberPoint.x, numberPoint.y + textPaint.textSize * 0.34f, textPaint,
                    )
                }

                val positionsByName = chart.positions.associateBy { it.name }
                chart.aspects.forEach { aspect ->
                    val first = positionsByName[aspect.bodyA] ?: return@forEach
                    val second = positionsByName[aspect.bodyB] ?: return@forEach
                    drawLine(
                        color = aspectLineColor(aspect.type).copy(alpha = 0.72f),
                        start = wheelPoint(center, aspectRadius, first.longitude, ascendantLongitude),
                        end = wheelPoint(center, aspectRadius, second.longitude, ascendantLongitude),
                        strokeWidth = if (aspect.orb <= 1.0) 1.8.dp.toPx() else 1.dp.toPx(),
                        cap = StrokeCap.Round,
                    )
                }

                chart.positions.forEach { point ->
                    val marker = wheelPoint(center, radius * 0.74f, point.longitude, ascendantLongitude)
                    val selected = selectedPoint?.name == point.name
                    drawCircle(
                        color = if (selected) Gold.copy(alpha = 0.28f) else surfaceColor,
                        radius = if (selected) 14.dp.toPx() else 11.dp.toPx(),
                        center = marker,
                    )
                    if (selected) drawCircle(Gold, 14.dp.toPx(), marker, style = Stroke(1.5.dp.toPx()))
                    textPaint.color = if (selected) Gold.toArgb() else textColor.toArgb()
                    textPaint.textSize = 18.sp.toPx()
                    drawContext.canvas.nativeCanvas.drawText(
                        planetSymbol(point.name), marker.x, marker.y + textPaint.textSize * 0.34f, textPaint,
                    )
                }

                drawLine(Gold, Offset(center.x - radius, center.y), Offset(center.x + radius, center.y), 1.dp.toPx())
                textPaint.color = Gold.toArgb()
                textPaint.textSize = 10.sp.toPx()
                textPaint.textAlign = android.graphics.Paint.Align.LEFT
                drawContext.canvas.nativeCanvas.drawText("ASC", center.x - radius + 5.dp.toPx(), center.y - 5.dp.toPx(), textPaint)
                textPaint.textAlign = android.graphics.Paint.Align.CENTER
            }

            Row(
                modifier = Modifier.fillMaxWidth().padding(top = 8.dp),
                horizontalArrangement = Arrangement.SpaceEvenly,
            ) {
                AspectLegend("Uyumlu", Color(0xFF4F9D78))
                AspectLegend("Zorlayıcı", Color(0xFFD35D6E))
                AspectLegend("Kavuşum", Gold)
            }

            selectedPoint?.let { point ->
                Card(
                    modifier = Modifier.fillMaxWidth().padding(top = 12.dp),
                    colors = CardDefaults.cardColors(containerColor = PrimaryPurple.copy(alpha = 0.08f)),
                    shape = RoundedCornerShape(12.dp),
                ) {
                    Row(Modifier.fillMaxWidth().padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
                        Text(planetSymbol(point.name), color = Gold, fontSize = 28.sp)
                        Column(Modifier.padding(start = 10.dp).weight(1f)) {
                            Text(planetName(point.name), fontWeight = FontWeight.SemiBold)
                            Text(
                                "${signName(point.sign)} ${formatDegree(point.degreeInSign)} · ${point.house?.let { "$it. ev" } ?: "Ev yok"}",
                                color = subtleTextColor,
                                style = MaterialTheme.typography.bodySmall,
                            )
                        }
                        if (point.isRetrograde) Text("R", color = PrimaryPurple, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
    }
}

@Composable
private fun AspectLegend(label: String, color: Color) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Box(Modifier.size(8.dp).background(color, CircleShape))
        Text(label, modifier = Modifier.padding(start = 5.dp), fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

private val zodiacSymbols = listOf("♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓")
private val zodiacKeys = listOf("aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces")

private fun zodiacLongitude(sign: String, degree: Double): Double =
    ((zodiacKeys.indexOf(sign.lowercase(Locale.ROOT)).coerceAtLeast(0) * 30.0 + degree) % 360.0 + 360.0) % 360.0

private fun wheelPoint(center: Offset, radius: Float, longitude: Double, ascendant: Double): Offset {
    val angle = (180.0 - (longitude - ascendant)) * PI / 180.0
    return Offset(center.x + cos(angle).toFloat() * radius, center.y + sin(angle).toFloat() * radius)
}

private fun distance(first: Offset, second: Offset): Float =
    sqrt((first.x - second.x) * (first.x - second.x) + (first.y - second.y) * (first.y - second.y))

private fun circularMidpoint(first: Double, second: Double): Double {
    var span = (second - first + 360.0) % 360.0
    if (span == 0.0) span = 30.0
    return (first + span / 2.0) % 360.0
}

private fun zodiacColor(index: Int): Color = when (index % 4) {
    0 -> Color(0xFFE86A52)
    1 -> Color(0xFF4F9D78)
    2 -> Color(0xFFE0A72E)
    else -> Color(0xFF4F82C0)
}

private fun aspectLineColor(type: String): Color = when (type.lowercase(Locale.ROOT)) {
    "trine", "sextile" -> Color(0xFF4F9D78)
    "square", "opposition" -> Color(0xFFD35D6E)
    "conjunction" -> Gold
    else -> Color(0xFF8C72B8)
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

private fun formatDateInput(previous: String = "", value: String): String {
    if (value.length < previous.length && previous.endsWith('.') && value == previous.dropLast(1)) {
        return formatDateInput(value = value.dropLast(1))
    }
    val digits = value.filter(Char::isDigit).take(8)
    return buildString {
        digits.forEachIndexed { index, char ->
            if (index == 2 || index == 4) append('.')
            append(char)
        }
    }
}

private fun formatTimeInput(previous: String = "", value: String): String {
    if (value.length < previous.length && previous.endsWith(':') && value == previous.dropLast(1)) {
        return formatTimeInput(value = value.dropLast(1))
    }
    val digits = value.filter(Char::isDigit).take(4)
    return buildString {
        digits.forEachIndexed { index, char ->
            if (index == 2) append(':')
            append(char)
        }
    }
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
