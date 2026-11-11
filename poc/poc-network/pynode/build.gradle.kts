plugins {
    id("com.android.application") version "8.9.3" apply false
    id("org.jetbrains.kotlin.android") version "2.1.21" apply false
    // 16.1.x et non 17.x : 17 exige que le Python du PC ait la même version que celui
    // de l'appli (3.11 ici), et 3.11 est la dernière version qui supporte armeabi-v7a.
    id("com.chaquo.python") version "16.1.0" apply false
}
