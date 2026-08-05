package com.olimora.app.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

private val DarkColorScheme = darkColorScheme(
    primary = PrimaryPurpleLight,
    onPrimary = NightBackground,
    background = NightBackground,
    onBackground = NightText,
    surface = NightSurface,
    onSurface = NightText,
    surfaceVariant = SoftSurface,
    onSurfaceVariant = NightMuted,
    outline = NightOutline,
)

private val LightColorScheme = lightColorScheme(
    primary = PrimaryPurple,
    onPrimary = DaySurface,
    background = DayBackground,
    onBackground = DayText,
    surface = DaySurface,
    onSurface = DayText,
    surfaceVariant = DaySoftSurface,
    onSurfaceVariant = DayMuted,
    outline = DayOutline,
)

@Composable
fun OlimoraTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit,
) {
    MaterialTheme(
        colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme,
        typography = Typography,
        content = content,
    )
}
