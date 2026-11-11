plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("com.chaquo.python")
}

android {
    namespace = "ch.phonedc.pynode"
    compileSdk = 35

    defaultConfig {
        applicationId = "ch.phonedc.pynode"
        minSdk = 24 // Android 7.0, minimum de Chaquopy 16
        targetSdk = 35
        versionCode = 1
        versionName = "0.1"
        ndk {
            // armeabi-v7a : vieux téléphones 32 bits (Galaxy A5 2016) ; x86_64 : émulateur
            abiFilters += listOf("armeabi-v7a", "arm64-v8a", "x86_64")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
}

chaquopy {
    defaultConfig {
        version = "3.11" // dernière version de Python avec armeabi-v7a
        pip {
            // Embarqués dans l'APK. D'autres paquets pur Python peuvent être ajoutés
            // sans recompiler, dans <dossier de l'appli>/site-packages (voir README).
            install("flask>=3,<4")
            install("django>=5.1,<5.2")
        }
        // Django lit ses templates/locales sur le disque : il doit être extrait de l'APK.
        extractPackages("django")
    }
}

// Page web du nœud : on réutilise ../phone/index.html (version Termux) pour n'avoir
// qu'un seul fichier à maintenir ; copiée dans le paquet Python à chaque build.
val copyNodePage by tasks.registering(Copy::class) {
    from("../../phone/index.html")
    into("src/main/python/pynode")
}
tasks.matching { it.name.matches(Regex("merge\\w*PythonSources")) }.configureEach { dependsOn(copyNodePage) }

dependencies {
    implementation("androidx.core:core-ktx:1.15.0")
}
