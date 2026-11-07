import 'package:flutter/material.dart';
import 'screens/home_screen.dart';
import 'state/app_state.dart';

class MuseumGuideApp extends StatefulWidget {
  const MuseumGuideApp({super.key});

  @override
  State<MuseumGuideApp> createState() => _MuseumGuideAppState();
}

class _MuseumGuideAppState extends State<MuseumGuideApp> {
  late final AppState _appState;

  @override
  void initState() {
    super.initState();
    _appState = AppState();
  }

  @override
  void dispose() {
    _appState.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final baseTextTheme = ThemeData(
      brightness: Brightness.dark,
      useMaterial3: true,
    ).textTheme;

    return AppStateScope(
      notifier: _appState,
      child: MaterialApp(
        title: 'Museo - Hướng Dẫn Bảo Tàng',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          useMaterial3: true,
          scaffoldBackgroundColor: const Color(0xFF121212),
          colorScheme: const ColorScheme(
            brightness: Brightness.dark,
            primary: Color(0xFFEAC0A2), // Copper / Champagne chính
            onPrimary: Color(0xFF121212),
            primaryContainer: Color(0xFF2A2A2A),
            onPrimaryContainer: Color(0xFFEAC0A2),
            secondary: Color(0xFFB89780), // Copper Dark
            onSecondary: Color(0xFF121212),
            secondaryContainer: Color(0xFF1E1E1E),
            onSecondaryContainer: Color(0xFFEAC0A2),
            surface: Color(0xFF1A1A1A),
            onSurface: Colors.white,
            surfaceContainerHighest: Color(0xFF222222),
            onSurfaceVariant: Color(0xFF8E8E93), // Slate gray
            outline: Color(0xFF2A2A2A),
            outlineVariant: Color(0xFF333333),
            error: Color(0xFFCF6679),
            onError: Color(0xFF121212),
          ),
          appBarTheme: const AppBarTheme(
            backgroundColor: Color(0xFF121212),
            foregroundColor: Colors.white,
            elevation: 0,
            scrolledUnderElevation: 0,
            centerTitle: false,
            titleTextStyle: TextStyle(
              color: Colors.white,
              fontFamily: 'serif',
              fontSize: 20,
              fontWeight: FontWeight.w500,
            ),
          ),
          textTheme: baseTextTheme.copyWith(
            displayLarge:
                baseTextTheme.displayLarge?.copyWith(fontFamily: 'serif'),
            displayMedium:
                baseTextTheme.displayMedium?.copyWith(fontFamily: 'serif'),
            displaySmall:
                baseTextTheme.displaySmall?.copyWith(fontFamily: 'serif'),
            headlineLarge:
                baseTextTheme.headlineLarge?.copyWith(fontFamily: 'serif'),
            headlineMedium:
                baseTextTheme.headlineMedium?.copyWith(fontFamily: 'serif'),
            headlineSmall:
                baseTextTheme.headlineSmall?.copyWith(fontFamily: 'serif'),
          ),
          snackBarTheme: const SnackBarThemeData(
            backgroundColor: Color(0xFF242424),
            contentTextStyle: TextStyle(color: Colors.white),
            behavior: SnackBarBehavior.floating,
          ),
          cardTheme: CardThemeData(
            color: const Color(0xFF1A1A1A),
            elevation: 0,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(20),
              side: const BorderSide(color: Color(0xFF2A2A2A), width: 1),
            ),
          ),
        ),
        home: const HomeScreen(),
      ),
    );
  }
}
