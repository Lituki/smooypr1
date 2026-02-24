-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 13-05-2025 a las 11:37:58
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `smooydb`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `avisos`
--

CREATE TABLE `avisos` (
  `id` int(11) NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `categoria` varchar(100) DEFAULT NULL,
  `descripcion` text DEFAULT NULL,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `establecimiento_id` int(11) DEFAULT NULL,
  `usuario_id` int(11) DEFAULT NULL,
  `estado` varchar(50) DEFAULT NULL,
  `proceso_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `avisos`
--

INSERT INTO `avisos` (`id`, `nombre`, `categoria`, `descripcion`, `fecha_creacion`, `establecimiento_id`, `usuario_id`, `estado`, `proceso_id`) VALUES
(35, 'Revisión necesaria: Revisión de inventario (ID: 93)', 'Transcurso de la jornada', 'Problema en la tarea: Revisión de inventario (verificado: 07/05/2025 14:25)\n\nDetalles de la tarea:\nEstado del proceso: Verificación pendiente\nID del proceso: 93\nDescripción: Comprobar niveles de inventario\n\nPor favor, corrija los siguientes problemas:', '2025-05-07 12:25:49', 2, 1, 'Pendiente', 93),
(36, 'Revisión necesaria: Cerrar caja (ID: 105)', 'Cierre', 'Problema en la tarea: Cerrar caja (verificado: 08/05/2025 13:11)\n\nDetalles de la tarea:\nEstado del proceso: Verificación pendiente\nID del proceso: 105\nDescripción: Realizar cierre y conteo de caja\n\nPor favor, corrija los siguientes problemas:', '2025-05-08 11:11:15', 2, 1, 'Pendiente', 105),
(38, 'Revisión necesaria: Desactivar alarma (ID: 101)', 'Apertura', 'Problema en la tarea: Desactivar alarma (verificado: 08/05/2025 14:23)\n\nDetalles de la tarea:\nEstado del proceso: Verificación pendiente\nID del proceso: 101\nDescripción: Desactivar sistema de alarma al llegar\n\nPor favor, corrija los siguientes problemas:', '2025-05-08 12:24:12', 2, 1, 'Completado', 101);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `aviso_comentarios`
--

CREATE TABLE `aviso_comentarios` (
  `id` int(11) NOT NULL,
  `aviso_id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `comentario` text NOT NULL,
  `fecha_creacion` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `aviso_imagenes`
--

CREATE TABLE `aviso_imagenes` (
  `id` int(11) NOT NULL,
  `aviso_id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `ruta_imagen` varchar(255) NOT NULL,
  `nombre_imagen` varchar(255) NOT NULL,
  `fecha_subida` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `establecimientos`
--

CREATE TABLE `establecimientos` (
  `id` int(11) NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `direccion` varchar(255) DEFAULT NULL,
  `tipo` varchar(100) DEFAULT NULL,
  `estado` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `establecimientos`
--

INSERT INTO `establecimientos` (`id`, `nombre`, `direccion`, `tipo`, `estado`) VALUES
(1, 'Barcelona', 'Carrer de Exemple, 123', 'Oficina', 'Activo'),
(2, 'Murcia', 'Calle Alfonso X', 'Oficina', 'Activo'),
(15, 'Galicia', 'Nose', 'Cafetería', 'Activo'),
(18, 'Valencia', 'Virgen', 'SMÖOY YOGUR', 'Activo');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `procesos2`
--

CREATE TABLE `procesos2` (
  `id` int(11) NOT NULL,
  `tipo_proceso` varchar(255) DEFAULT NULL,
  `descripcion` text DEFAULT NULL,
  `frecuencia` varchar(100) DEFAULT NULL,
  `horario` varchar(100) DEFAULT NULL,
  `fecha_inicio` date DEFAULT NULL,
  `fecha_fin` date DEFAULT NULL,
  `estado` varchar(50) DEFAULT NULL,
  `ubicacion` varchar(255) DEFAULT NULL,
  `establecimiento_id` int(11) DEFAULT NULL,
  `usuario_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `procesos2`
--

INSERT INTO `procesos2` (`id`, `tipo_proceso`, `descripcion`, `frecuencia`, `horario`, `fecha_inicio`, `fecha_fin`, `estado`, `ubicacion`, `establecimiento_id`, `usuario_id`) VALUES
(12, 'CIERRE', 'Proceso de CIERRE', 'Diaria', '7:00', '2025-04-11', '2025-04-11', 'Verificación pendiente', 'Barcelona', 1, NULL),
(13, 'TRASCURSO DE JORNADA', 'Proceso de TRASCURSO DE JORNADA', 'Diaria', '7:00', '2025-04-11', '2025-04-11', 'Verificación pendiente', 'Barcelona', 1, NULL),
(15, 'CIERRE', 'Proceso de CIERRE', 'Diaria', '7:00', '2025-04-11', '2025-04-11', 'Verificación pendiente', 'Murcia', 2, NULL),
(16, 'TRASCURSO DE JORNADA', 'Proceso de TRASCURSO DE JORNADA', 'Diaria', '7:00', '2025-04-11', '2025-04-11', 'Verificación pendiente', 'Murcia', 2, NULL),
(24, 'APERTURA', 'Proceso de APERTURA', 'Diaria', '07:00', '2025-04-28', '2025-04-28', 'Verificación pendiente', 'Barcelona', 1, NULL),
(25, 'CIERRE', 'Proceso de CIERRE', 'Diaria', '7:00', '2025-04-28', '2025-04-28', 'Verificación pendiente', 'Barcelona', 1, NULL),
(26, 'TRASCURSO DE JORNADA', 'Proceso de TRASCURSO DE JORNADA', 'Diaria', '7:00', '2025-04-28', '2025-04-28', 'Verificación pendiente', 'Barcelona', 1, NULL),
(27, 'APERTURA', 'Proceso de APERTURA', 'Diaria', '07:00', '2025-04-28', '2025-04-28', 'Verificación pendiente', 'Murcia', 2, NULL),
(28, 'CIERRE', 'Proceso de CIERRE', 'Diaria', '7:00', '2025-04-28', '2025-04-28', 'Verificación pendiente', 'Murcia', 2, NULL),
(29, 'TRASCURSO DE JORNADA', 'Proceso de TRASCURSO DE JORNADA', 'Diaria', '7:00', '2025-04-28', '2025-04-28', 'Verificación pendiente', 'Murcia', 2, NULL),
(30, 'APERTURA', 'Proceso de APERTURA', 'Diaria', '07:00', '2025-04-28', '2025-04-28', 'Verificación pendiente', 'Galicia', 15, NULL),
(31, 'CIERRE', 'Proceso de CIERRE', 'Diaria', '7:00', '2025-04-28', '2025-04-28', 'Verificación pendiente', 'Galicia', 15, NULL),
(32, 'TRASCURSO DE JORNADA', 'Proceso de TRASCURSO DE JORNADA', 'Diaria', '7:00', '2025-04-28', '2025-04-28', 'Verificación pendiente', 'Galicia', 15, NULL),
(33, 'APERTURA', 'Proceso de APERTURA', 'Diaria', '07:00', '2025-04-28', '2025-04-28', 'Verificación pendiente', 'Valencia', 18, NULL),
(34, 'CIERRE', 'Proceso de CIERRE', 'Diaria', '7:00', '2025-04-28', '2025-04-28', 'Verificación pendiente', 'Valencia', 18, NULL),
(35, 'TRASCURSO DE JORNADA', 'Proceso de TRASCURSO DE JORNADA', 'Diaria', '7:00', '2025-04-28', '2025-04-28', 'Verificación pendiente', 'Valencia', 18, NULL),
(36, 'APERTURA', 'Proceso de APERTURA', 'Diaria', '07:00', '2025-04-29', '2025-04-29', 'Verificación pendiente', 'Barcelona', 1, NULL),
(37, 'CIERRE', 'Proceso de CIERRE', 'Diaria', '7:00', '2025-04-29', '2025-04-29', 'Verificación pendiente', 'Barcelona', 1, NULL),
(38, 'TRASCURSO DE JORNADA', 'Proceso de TRASCURSO DE JORNADA', 'Diaria', '7:00', '2025-04-29', '2025-04-29', 'Verificación pendiente', 'Barcelona', 1, NULL),
(39, 'APERTURA', 'Proceso de APERTURA', 'Diaria', '07:00', '2025-04-29', '2025-04-29', 'Verificación pendiente', 'Murcia', 2, NULL),
(40, 'CIERRE', 'Proceso de CIERRE', 'Diaria', '7:00', '2025-04-29', '2025-04-29', 'Verificación pendiente', 'Murcia', 2, NULL),
(41, 'TRASCURSO DE JORNADA', 'Proceso de TRASCURSO DE JORNADA', 'Diaria', '7:00', '2025-04-29', '2025-04-29', 'Verificación pendiente', 'Murcia', 2, NULL),
(42, 'APERTURA', 'Proceso de APERTURA', 'Diaria', '07:00', '2025-04-29', '2025-04-29', 'Verificación pendiente', 'Galicia', 15, NULL),
(43, 'CIERRE', 'Proceso de CIERRE', 'Diaria', '7:00', '2025-04-29', '2025-04-29', 'Verificación pendiente', 'Galicia', 15, NULL),
(44, 'TRASCURSO DE JORNADA', 'Proceso de TRASCURSO DE JORNADA', 'Diaria', '7:00', '2025-04-29', '2025-04-29', 'Verificación pendiente', 'Galicia', 15, NULL),
(45, 'APERTURA', 'Proceso de APERTURA', 'Diaria', '07:00', '2025-04-29', '2025-04-29', 'Verificación pendiente', 'Valencia', 18, NULL),
(46, 'CIERRE', 'Proceso de CIERRE', 'Diaria', '7:00', '2025-04-29', '2025-04-29', 'Verificación pendiente', 'Valencia', 18, NULL),
(47, 'TRASCURSO DE JORNADA', 'Proceso de TRASCURSO DE JORNADA', 'Diaria', '7:00', '2025-04-29', '2025-04-29', 'Completado', 'Valencia', 18, NULL),
(48, 'APERTURA', 'Proceso de APERTURA', 'Diaria', '07:00', '2025-04-30', '2025-04-30', 'Verificación pendiente', 'Barcelona', 1, NULL),
(49, 'CIERRE', 'Proceso de CIERRE', 'Diaria', '7:00', '2025-04-30', '2025-04-30', 'Completado', 'Barcelona', 1, NULL),
(50, 'TRASCURSO DE JORNADA', 'Proceso de TRASCURSO DE JORNADA', 'Diaria', '7:00', '2025-04-30', '2025-04-30', 'Completado', 'Barcelona', 1, NULL),
(51, 'APERTURA', 'Proceso de APERTURA', 'Diaria', '07:00', '2025-04-30', '2025-04-30', 'Verificación pendiente', 'Murcia', 2, NULL),
(52, 'CIERRE', 'Proceso de CIERRE', 'Diaria', '7:00', '2025-04-30', '2025-04-30', 'Completado', 'Murcia', 2, NULL),
(53, 'TRASCURSO DE JORNADA', 'Proceso de TRASCURSO DE JORNADA', 'Diaria', '7:00', '2025-04-30', '2025-04-30', 'Verificación pendiente', 'Murcia', 2, NULL),
(54, 'APERTURA', 'Proceso de APERTURA', 'Diaria', '07:00', '2025-04-30', '2025-04-30', 'Verificación pendiente', 'Galicia', 15, NULL),
(55, 'CIERRE', 'Proceso de CIERRE', 'Diaria', '7:00', '2025-04-30', '2025-04-30', 'Completado', 'Galicia', 15, NULL),
(56, 'TRASCURSO DE JORNADA', 'Proceso de TRASCURSO DE JORNADA', 'Diaria', '7:00', '2025-04-30', '2025-04-30', 'Verificación pendiente', 'Galicia', 15, NULL),
(57, 'APERTURA', 'Proceso de APERTURA', 'Diaria', '07:00', '2025-04-30', '2025-04-30', 'Completado', 'Valencia', 18, NULL),
(58, 'CIERRE', 'Proceso de CIERRE', 'Diaria', '7:00', '2025-04-30', '2025-04-30', 'Verificación pendiente', 'Valencia', 18, NULL),
(59, 'TRASCURSO DE JORNADA', 'Proceso de TRASCURSO DE JORNADA', 'Diaria', '7:00', '2025-04-30', '2025-04-30', 'Verificación pendiente', 'Valencia', 18, NULL),
(60, 'APERTURA', 'Proceso de APERTURA', 'Diaria', '07:00', '2025-05-05', '2025-05-05', 'Verificación pendiente', 'Barcelona', 1, NULL),
(61, 'CIERRE', 'Proceso de CIERRE', 'Diaria', '7:00', '2025-05-05', '2025-05-05', 'Verificación pendiente', 'Barcelona', 1, NULL),
(62, 'TRASCURSO DE JORNADA', 'Proceso de TRASCURSO DE JORNADA', 'Diaria', '7:00', '2025-05-05', '2025-05-05', 'Completado', 'Barcelona', 1, NULL),
(63, 'APERTURA', 'Proceso de APERTURA', 'Diaria', '07:00', '2025-05-05', '2025-05-05', 'Verificación pendiente', 'Murcia', 2, NULL),
(64, 'CIERRE', 'Proceso de CIERRE', 'Diaria', '7:00', '2025-05-05', '2025-05-05', 'Completado', 'Murcia', 2, NULL),
(65, 'TRASCURSO DE JORNADA', 'Proceso de TRASCURSO DE JORNADA', 'Diaria', '7:00', '2025-05-05', '2025-05-05', 'Verificación pendiente', 'Murcia', 2, NULL),
(66, 'APERTURA', 'Proceso de APERTURA', 'Diaria', '07:00', '2025-05-05', '2025-05-05', 'Verificación pendiente', 'Galicia', 15, NULL),
(67, 'CIERRE', 'Proceso de CIERRE', 'Diaria', '7:00', '2025-05-05', '2025-05-05', 'Verificación pendiente', 'Galicia', 15, NULL),
(68, 'TRASCURSO DE JORNADA', 'Proceso de TRASCURSO DE JORNADA', 'Diaria', '7:00', '2025-05-05', '2025-05-05', 'Verificación pendiente', 'Galicia', 15, NULL),
(69, 'APERTURA', 'Proceso de APERTURA', 'Diaria', '07:00', '2025-05-05', '2025-05-05', 'Verificación pendiente', 'Valencia', 18, NULL),
(70, 'CIERRE', 'Proceso de CIERRE', 'Diaria', '7:00', '2025-05-05', '2025-05-05', 'Verificación pendiente', 'Valencia', 18, NULL),
(71, 'TRASCURSO DE JORNADA', 'Proceso de TRASCURSO DE JORNADA', 'Diaria', '7:00', '2025-05-05', '2025-05-05', 'Verificación pendiente', 'Valencia', 18, NULL),
(72, 'APERTURA', 'bbbcncncj', 'Diaria', '09:41', '2025-05-05', '2025-05-05', 'Verificación pendiente', NULL, 1, NULL),
(73, 'APERTURA', 'Proceso de APERTURA', 'Diaria', '07:00', '2025-05-06', '2025-05-06', 'Verificación pendiente', 'Barcelona', 1, NULL),
(74, 'CIERRE', 'Proceso de CIERRE', 'Diaria', '7:00', '2025-05-06', '2025-05-06', 'Verificación pendiente', 'Barcelona', 1, NULL),
(75, 'TRASCURSO DE JORNADA', 'Proceso de TRASCURSO DE JORNADA', 'Diaria', '7:00', '2025-05-06', '2025-05-06', 'Verificación pendiente', 'Barcelona', 1, NULL),
(76, 'APERTURA', 'Proceso de APERTURA', 'Diaria', '07:00', '2025-05-06', '2025-05-06', 'Verificación pendiente', 'Murcia', 2, NULL),
(77, 'CIERRE', 'Proceso de CIERRE', 'Diaria', '7:00', '2025-05-06', '2025-05-06', 'Verificación pendiente', 'Murcia', 2, NULL),
(78, 'TRASCURSO DE JORNADA', 'Proceso de TRASCURSO DE JORNADA', 'Diaria', '7:00', '2025-05-06', '2025-05-06', 'Completado', 'Murcia', 2, NULL),
(79, 'APERTURA', 'Proceso de APERTURA', 'Diaria', '07:00', '2025-05-06', '2025-05-06', 'Verificación pendiente', 'Galicia', 15, NULL),
(80, 'CIERRE', 'Proceso de CIERRE', 'Diaria', '7:00', '2025-05-06', '2025-05-06', 'Verificación pendiente', 'Galicia', 15, NULL),
(81, 'TRASCURSO DE JORNADA', 'Proceso de TRASCURSO DE JORNADA', 'Diaria', '7:00', '2025-05-06', '2025-05-06', 'Verificación pendiente', 'Galicia', 15, NULL),
(82, 'APERTURA', 'Proceso de APERTURA', 'Diaria', '07:00', '2025-05-06', '2025-05-06', 'Verificación pendiente', 'Valencia', 18, NULL),
(83, 'CIERRE', 'Proceso de CIERRE', 'Diaria', '7:00', '2025-05-06', '2025-05-06', 'Verificación pendiente', 'Valencia', 18, NULL),
(84, 'TRASCURSO DE JORNADA', 'Proceso de TRASCURSO DE JORNADA', 'Diaria', '7:00', '2025-05-06', '2025-05-06', 'Verificación pendiente', 'Valencia', 18, NULL),
(85, 'APERTURA', 'Proceso de APERTURA', 'Diaria', '07:00', '2025-05-07', '2025-05-07', 'Verificación pendiente', 'Barcelona', 1, NULL),
(88, 'APERTURA', 'Proceso de APERTURA', 'Diaria', '07:00', '2025-05-07', '2025-05-07', 'Verificación pendiente', 'Murcia', 2, NULL),
(90, 'TRASCURSO DE JORNADA', 'Proceso de TRASCURSO DE JORNADA', 'Diaria', '7:00', '2025-05-07', '2025-05-07', 'Verificado', 'Murcia', 2, NULL),
(91, 'APERTURA', 'Proceso de APERTURA', 'Diaria', '07:00', '2025-05-07', '2025-05-07', 'Verificación pendiente', 'Galicia', 15, NULL),
(92, 'CIERRE', 'Proceso de CIERRE', 'Diaria', '7:00', '2025-05-07', '2025-05-07', 'Completado', 'Galicia', 15, NULL),
(93, 'TRASCURSO DE JORNADA', 'Proceso de TRASCURSO DE JORNADA', 'Diaria', '7:00', '2025-05-07', '2025-05-07', 'Verificación pendiente', 'Galicia', 15, NULL),
(94, 'APERTURA', 'Proceso de APERTURA', 'Diaria', '07:00', '2025-05-07', '2025-05-07', 'Verificación pendiente', 'Valencia', 18, NULL),
(95, 'CIERRE', 'Proceso de CIERRE', 'Diaria', '7:00', '2025-05-07', '2025-05-07', 'Verificación pendiente', 'Valencia', 18, NULL),
(96, 'TRASCURSO DE JORNADA', 'Proceso de TRASCURSO DE JORNADA', 'Diaria', '7:00', '2025-05-07', '2025-05-07', 'Verificación pendiente', 'Valencia', 18, NULL),
(97, 'TRASCURSO DE LA JORNADA', 'mepicaelpene', 'Diaria', '11:45', '2025-05-07', '0000-00-00', 'Verificación pendiente', NULL, 15, NULL),
(98, 'APERTURA', 'Proceso de APERTURA', 'Diaria', '07:00', '2025-05-08', '2025-05-08', 'Verificación pendiente', 'Barcelona', 1, NULL),
(99, 'CIERRE', 'Proceso de CIERRE', 'Diaria', '7:00', '2025-05-08', '2025-05-08', 'Verificación pendiente', 'Barcelona', 1, NULL),
(100, 'TRASCURSO DE JORNADA', 'Proceso de TRASCURSO DE JORNADA', 'Diaria', '7:00', '2025-05-08', '2025-05-08', 'Verificación pendiente', 'Barcelona', 1, NULL),
(101, 'APERTURA', 'Proceso de APERTURA', 'Diaria', '07:00', '2025-05-08', '2025-05-08', 'Verificación pendiente', 'Murcia', 2, NULL),
(102, 'CIERRE', 'Proceso de CIERRE', 'Diaria', '7:00', '2025-05-08', '2025-05-08', 'Verificación pendiente', 'Murcia', 2, NULL),
(103, 'TRASCURSO DE JORNADA', 'Proceso de TRASCURSO DE JORNADA', 'Diaria', '7:00', '2025-05-08', '2025-05-08', 'Verificación pendiente', 'Murcia', 2, NULL),
(104, 'APERTURA', 'Proceso de APERTURA', 'Diaria', '07:00', '2025-05-08', '2025-05-08', 'Verificación pendiente', 'Galicia', 15, NULL),
(105, 'CIERRE', 'Proceso de CIERRE', 'Diaria', '7:00', '2025-05-08', '2025-05-08', 'Completado', 'Galicia', 15, NULL),
(106, 'TRASCURSO DE JORNADA', 'Proceso de TRASCURSO DE JORNADA', 'Diaria', '7:00', '2025-05-08', '2025-05-08', 'Verificación pendiente', 'Galicia', 15, NULL),
(107, 'APERTURA', 'Proceso de APERTURA', 'Diaria', '07:00', '2025-05-08', '2025-05-08', 'Verificación pendiente', 'Valencia', 18, NULL),
(108, 'CIERRE', 'Proceso de CIERRE', 'Diaria', '7:00', '2025-05-08', '2025-05-08', 'Verificación pendiente', 'Valencia', 18, NULL),
(109, 'TRASCURSO DE JORNADA', 'Proceso de TRASCURSO DE JORNADA', 'Diaria', '7:00', '2025-05-08', '2025-05-08', 'Verificación pendiente', 'Valencia', 18, NULL),
(110, 'APERTURA', 'ola Jonathan', 'Diaria', '09:03', '2025-05-12', '0000-00-00', 'No finalizado', NULL, 18, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `proceso_comentarios`
--

CREATE TABLE `proceso_comentarios` (
  `id` int(11) NOT NULL,
  `proceso_id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `texto` text NOT NULL,
  `fecha` datetime NOT NULL,
  `fecha_creacion` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `proceso_comentarios`
--

INSERT INTO `proceso_comentarios` (`id`, `proceso_id`, `usuario_id`, `texto`, `fecha`, `fecha_creacion`) VALUES
(5, 74, 1, 'hola', '0000-00-00 00:00:00', '2025-05-06 10:26:41'),
(6, 99, 1, 'hola', '0000-00-00 00:00:00', '2025-05-12 09:00:21'),
(7, 99, 1, 'que tal', '0000-00-00 00:00:00', '2025-05-12 09:00:38');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `proceso_imagenes`
--

CREATE TABLE `proceso_imagenes` (
  `id` int(11) NOT NULL,
  `proceso_id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `ruta_imagen` varchar(255) NOT NULL,
  `fecha` datetime NOT NULL,
  `fecha_subida` datetime DEFAULT current_timestamp(),
  `nombre_imagen` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `proceso_tareas`
--

CREATE TABLE `proceso_tareas` (
  `id` int(11) NOT NULL,
  `proceso_id` int(11) NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `orden` int(11) DEFAULT 0,
  `estado` varchar(50) DEFAULT 'Pendiente',
  `fecha_creacion` datetime DEFAULT current_timestamp(),
  `fecha_completado` datetime DEFAULT NULL,
  `usuario_completado_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `proceso_tareas`
--

INSERT INTO `proceso_tareas` (`id`, `proceso_id`, `nombre`, `descripcion`, `orden`, `estado`, `fecha_creacion`, `fecha_completado`, `usuario_completado_id`) VALUES
(51, 12, 'Cerrar caja', 'Realizar cierre y conteo de caja', 1, 'Pendiente', '2025-04-11 09:40:42', '2025-04-11 09:41:33', 1),
(52, 12, 'Limpieza de cierre', 'Limpieza general del local', 2, 'Pendiente', '2025-04-11 09:40:42', '2025-04-11 11:18:20', 1),
(53, 12, 'Apagar equipos', 'Apagar todos los equipos electrónicos', 3, 'Pendiente', '2025-04-11 09:40:42', NULL, NULL),
(54, 12, 'Apagar luces', 'Apagar todas las luces', 4, 'Pendiente', '2025-04-11 09:40:42', NULL, NULL),
(55, 12, 'Activar alarma', 'Activar sistema de alarma al salir', 5, 'Pendiente', '2025-04-11 09:40:42', NULL, NULL),
(56, 15, 'Cerrar caja', 'Realizar cierre y conteo de caja', 1, 'Completada', '2025-04-11 10:16:04', '2025-04-11 10:16:07', 1),
(57, 15, 'Limpieza de cierre', 'Limpieza general del local', 2, 'Completada', '2025-04-11 10:16:04', '2025-04-11 10:16:08', 1),
(58, 15, 'Apagar equipos', 'Apagar todos los equipos electrónicos', 3, 'Completada', '2025-04-11 10:16:04', '2025-04-11 10:16:08', 1),
(59, 15, 'Apagar luces', 'Apagar todas las luces', 4, 'Completada', '2025-04-11 10:16:04', '2025-04-11 10:16:09', 1),
(60, 15, 'Activar alarma', 'Activar sistema de alarma al salir', 5, 'Completada', '2025-04-11 10:16:04', '2025-04-11 10:16:09', 1),
(64, 25, 'Cerrar caja', 'Realizar cierre y conteo de caja', 1, 'Completada', '2025-04-28 10:12:56', '2025-04-28 11:22:56', 1),
(65, 25, 'Limpieza de cierre', 'Limpieza general del local', 2, 'Completada', '2025-04-28 10:12:56', '2025-04-28 11:23:09', 1),
(66, 25, 'Apagar equipos', 'Apagar todos los equipos electrónicos', 3, 'Completada', '2025-04-28 10:12:56', '2025-04-28 11:23:11', 1),
(67, 25, 'Apagar luces', 'Apagar todas las luces', 4, 'Completada', '2025-04-28 10:12:56', '2025-04-28 11:23:13', 1),
(68, 25, 'Activar alarma', 'Activar sistema de alarma al salir', 5, 'Completada', '2025-04-28 10:12:56', '2025-04-28 11:23:13', 1),
(69, 29, 'Revisión de inventario', 'Comprobar niveles de inventario', 1, 'Pendiente', '2025-04-28 10:13:10', NULL, NULL),
(70, 29, 'Limpieza de áreas comunes', 'Mantener áreas comunes limpias', 2, 'Pendiente', '2025-04-28 10:13:10', NULL, NULL),
(71, 29, 'Control de temperatura', 'Verificar temperaturas de equipos', 3, 'Pendiente', '2025-04-28 10:13:10', NULL, NULL),
(72, 40, 'Cerrar caja', 'Realizar cierre y conteo de caja', 1, 'Pendiente', '2025-04-30 10:10:50', '2025-04-30 10:11:01', 1),
(73, 40, 'Limpieza de cierre', 'Limpieza general del local', 2, 'Pendiente', '2025-04-30 10:10:50', '2025-04-30 10:11:01', 1),
(74, 40, 'Apagar equipos', 'Apagar todos los equipos electrónicos', 3, 'Pendiente', '2025-04-30 10:10:50', '2025-04-30 10:11:02', 1),
(75, 40, 'Apagar luces', 'Apagar todas las luces', 4, 'Pendiente', '2025-04-30 10:10:50', '2025-04-30 10:11:04', 1),
(76, 40, 'Activar alarma', 'Activar sistema de alarma al salir', 5, 'Pendiente', '2025-04-30 10:10:50', '2025-04-30 10:11:04', 1),
(77, 50, 'Revisión de inventario', 'Comprobar niveles de inventario', 1, 'Completada', '2025-04-30 10:20:47', '2025-04-30 11:24:04', 1),
(78, 50, 'Limpieza de áreas comunes', 'Mantener áreas comunes limpias', 2, 'Completada', '2025-04-30 10:20:47', '2025-04-30 10:28:43', 1),
(79, 50, 'Control de temperatura', 'Verificar temperaturas de equipos', 3, 'Completada', '2025-04-30 10:20:47', '2025-04-30 10:28:44', 1),
(80, 49, 'Cerrar caja', 'Realizar cierre y conteo de caja', 1, 'Completada', '2025-04-30 10:33:55', '2025-05-05 08:12:34', 1),
(81, 49, 'Limpieza de cierre', 'Limpieza general del local', 2, 'Completada', '2025-04-30 10:33:55', '2025-04-30 12:59:16', 1),
(82, 49, 'Apagar equipos', 'Apagar todos los equipos electrónicos', 3, 'Pendiente', '2025-04-30 10:33:55', '2025-04-30 13:12:35', 1),
(83, 49, 'Apagar luces', 'Apagar todas las luces', 4, 'Completada', '2025-04-30 10:33:55', '2025-04-30 13:12:36', 1),
(84, 49, 'Activar alarma', 'Activar sistema de alarma al salir', 5, 'Completada', '2025-04-30 10:33:55', '2025-04-30 13:12:41', 1),
(85, 52, 'Cerrar caja', 'Realizar cierre y conteo de caja', 1, 'Completada', '2025-04-30 11:24:20', '2025-04-30 11:24:26', 1),
(86, 52, 'Limpieza de cierre', 'Limpieza general del local', 2, 'Completada', '2025-04-30 11:24:20', '2025-04-30 11:24:25', 1),
(87, 52, 'Apagar equipos', 'Apagar todos los equipos electrónicos', 3, 'Completada', '2025-04-30 11:24:20', '2025-04-30 11:24:25', 1),
(88, 52, 'Apagar luces', 'Apagar todas las luces', 4, 'Completada', '2025-04-30 11:24:20', '2025-04-30 11:24:24', 1),
(89, 52, 'Activar alarma', 'Activar sistema de alarma al salir', 5, 'Completada', '2025-04-30 11:24:20', '2025-04-30 11:24:24', 1),
(90, 55, 'Cerrar caja', 'Realizar cierre y conteo de caja', 1, 'Completada', '2025-04-30 11:29:04', '2025-04-30 11:29:06', 1),
(91, 55, 'Limpieza de cierre', 'Limpieza general del local', 2, 'Completada', '2025-04-30 11:29:04', '2025-04-30 11:29:07', 1),
(92, 55, 'Apagar equipos', 'Apagar todos los equipos electrónicos', 3, 'Completada', '2025-04-30 11:29:04', '2025-04-30 11:29:07', 1),
(93, 55, 'Apagar luces', 'Apagar todas las luces', 4, 'Completada', '2025-04-30 11:29:04', '2025-04-30 11:29:08', 1),
(94, 55, 'Activar alarma', 'Activar sistema de alarma al salir', 5, 'Completada', '2025-04-30 11:29:04', '2025-04-30 11:29:10', 1),
(95, 47, 'Revisión de inventario', 'Comprobar niveles de inventario', 1, 'Completada', '2025-04-30 12:59:32', '2025-04-30 12:59:34', 1),
(96, 47, 'Limpieza de áreas comunes', 'Mantener áreas comunes limpias', 2, 'Completada', '2025-04-30 12:59:32', '2025-04-30 12:59:34', 1),
(97, 47, 'Control de temperatura', 'Verificar temperaturas de equipos', 3, 'Completada', '2025-04-30 12:59:32', '2025-04-30 12:59:35', 1),
(98, 57, 'Desactivar alarma', 'Desactivar sistema de alarma al llegar', 1, 'Completada', '2025-04-30 13:24:51', '2025-04-30 13:25:02', 1),
(99, 57, 'Encender luces', 'Encender todas las luces del local', 2, 'Completada', '2025-04-30 13:24:51', '2025-04-30 13:25:03', 1),
(100, 57, 'Verificar equipos', 'Comprobar que todos los equipos funcionan correctamente', 3, 'Completada', '2025-04-30 13:24:51', '2025-04-30 13:25:06', 1),
(101, 57, 'Preparar caja', 'Preparar la caja registradora con cambio', 4, 'Completada', '2025-04-30 13:24:51', '2025-04-30 13:25:07', 1),
(102, 57, 'Limpieza inicial', 'Realizar limpieza rápida del área de atención', 5, 'Completada', '2025-04-30 13:24:51', '2025-04-30 13:25:08', 1),
(103, 62, 'Revisión de inventario', 'Comprobar niveles de inventario', 1, 'Completada', '2025-05-05 09:32:55', '2025-05-05 11:52:32', 1),
(104, 62, 'Limpieza de áreas comunes', 'Mantener áreas comunes limpias', 2, 'Completada', '2025-05-05 09:32:55', '2025-05-05 10:16:26', 1),
(105, 62, 'Control de temperatura', 'Verificar temperaturas de equipos', 3, 'Completada', '2025-05-05 09:32:55', '2025-05-05 10:17:07', 1),
(106, 61, 'Cerrar caja', 'Realizar cierre y conteo de caja', 1, 'Pendiente', '2025-05-05 09:40:24', '2025-05-06 08:24:01', 1),
(107, 61, 'Limpieza de cierre', 'Limpieza general del local', 2, 'Completada', '2025-05-05 09:40:24', '2025-05-05 10:20:50', 1),
(108, 61, 'Apagar equipos', 'Apagar todos los equipos electrónicos', 3, 'Completada', '2025-05-05 09:40:24', '2025-05-05 09:59:14', 1),
(109, 61, 'Apagar luces', 'Apagar todas las luces', 4, 'Completada', '2025-05-05 09:40:24', '2025-05-05 09:59:14', 1),
(110, 61, 'Activar alarma', 'Activar sistema de alarma al salir', 5, 'Completada', '2025-05-05 09:40:24', '2025-05-05 09:59:11', 1),
(111, 64, 'Cerrar caja', 'Realizar cierre y conteo de caja', 1, 'Completada', '2025-05-05 10:21:01', '2025-05-05 10:21:04', 1),
(112, 64, 'Limpieza de cierre', 'Limpieza general del local', 2, 'Completada', '2025-05-05 10:21:01', '2025-05-05 10:21:04', 1),
(113, 64, 'Apagar equipos', 'Apagar todos los equipos electrónicos', 3, 'Completada', '2025-05-05 10:21:01', '2025-05-05 10:21:05', 1),
(114, 64, 'Apagar luces', 'Apagar todas las luces', 4, 'Completada', '2025-05-05 10:21:01', '2025-05-05 10:21:05', 1),
(115, 64, 'Activar alarma', 'Activar sistema de alarma al salir', 5, 'Verificación pendiente', '2025-05-05 10:21:01', '2025-05-05 10:21:24', 1),
(116, 61, 'Cagarse encima', 'snnsmflco', 6, 'Pendiente', '2025-05-06 08:42:14', NULL, NULL),
(117, 74, 'Cerrar caja', 'Realizar cierre y conteo de caja', 1, 'Completada', '2025-05-06 08:48:31', '2025-05-06 12:42:59', 2),
(118, 74, 'Limpieza de cierre', 'Limpieza general del local', 2, 'Completada', '2025-05-06 08:48:31', '2025-05-06 12:43:23', 2),
(119, 74, 'Apagar equipos', 'Apagar todos los equipos electrónicos', 3, 'Completada', '2025-05-06 08:48:31', '2025-05-06 12:43:33', 2),
(120, 74, 'Apagar luces', 'Apagar todas las luces', 4, 'Pendiente', '2025-05-06 08:48:31', '2025-05-06 12:43:42', 2),
(121, 74, 'Activar alarma', 'Activar sistema de alarma al salir', 5, 'Pendiente', '2025-05-06 08:48:31', '2025-05-06 12:43:43', 2),
(122, 78, 'Revisión de inventario', 'Comprobar niveles de inventario', 1, 'Completada', '2025-05-06 12:05:10', '2025-05-06 12:06:30', 1),
(123, 78, 'Limpieza de áreas comunes', 'Mantener áreas comunes limpias', 2, 'Completada', '2025-05-06 12:05:10', '2025-05-06 12:06:42', 1),
(124, 78, 'Control de temperatura', 'Verificar temperaturas de equipos', 3, 'Completada', '2025-05-06 12:05:10', '2025-05-06 12:06:44', 1),
(125, 83, 'Cerrar caja', 'Realizar cierre y conteo de caja', 1, 'Pendiente', '2025-05-06 12:09:09', NULL, NULL),
(126, 83, 'Limpieza de cierre', 'Limpieza general del local', 2, 'Pendiente', '2025-05-06 12:09:09', NULL, NULL),
(127, 83, 'Apagar equipos', 'Apagar todos los equipos electrónicos', 3, 'Pendiente', '2025-05-06 12:09:09', NULL, NULL),
(128, 83, 'Apagar luces', 'Apagar todas las luces', 4, 'Pendiente', '2025-05-06 12:09:09', NULL, NULL),
(129, 83, 'Activar alarma', 'Activar sistema de alarma al salir', 5, 'Pendiente', '2025-05-06 12:09:09', NULL, NULL),
(138, 92, 'Cerrar caja', 'Realizar cierre y conteo de caja', 1, 'Completada', '2025-05-07 12:51:26', '2025-05-07 13:23:11', 1),
(139, 92, 'Limpieza de cierre', 'Limpieza general del local', 2, 'Completada', '2025-05-07 12:51:26', '2025-05-07 13:23:12', 1),
(140, 92, 'Apagar equipos', 'Apagar todos los equipos electrónicos', 3, 'Completada', '2025-05-07 12:51:26', '2025-05-07 13:23:20', 1),
(141, 92, 'Apagar luces', 'Apagar todas las luces', 4, 'Completada', '2025-05-07 12:51:26', '2025-05-07 13:23:30', 1),
(142, 92, 'Activar alarma', 'Activar sistema de alarma al salir', 5, 'Completada', '2025-05-07 12:51:26', '2025-05-07 13:23:36', 1),
(143, 90, 'Revisión de inventario', 'Comprobar niveles de inventario', 1, 'Completada', '2025-05-07 12:51:39', '2025-05-08 08:28:16', 1),
(144, 90, 'Limpieza de áreas comunes', 'Mantener áreas comunes limpias', 2, 'Completada', '2025-05-07 12:51:39', '2025-05-07 12:51:40', 1),
(145, 90, 'Control de temperatura', 'Verificar temperaturas de equipos', 3, 'Completada', '2025-05-07 12:51:39', '2025-05-07 12:51:40', 1),
(146, 96, 'Revisión de inventario', 'Comprobar niveles de inventario', 1, 'Completada', '2025-05-07 13:02:19', '2025-05-07 13:02:21', 1),
(147, 96, 'Limpieza de áreas comunes', 'Mantener áreas comunes limpias', 2, 'Pendiente', '2025-05-07 13:02:19', NULL, NULL),
(148, 96, 'Control de temperatura', 'Verificar temperaturas de equipos', 3, 'Pendiente', '2025-05-07 13:02:19', NULL, NULL),
(149, 85, 'Desactivar alarma', 'Desactivar sistema de alarma al llegar', 1, 'Pendiente', '2025-05-07 13:28:13', '2025-05-07 14:57:44', 2),
(150, 85, 'Encender luces', 'Encender todas las luces del local', 2, 'Pendiente', '2025-05-07 13:28:13', '2025-05-07 13:28:15', 1),
(151, 85, 'Verificar equipos', 'Comprobar que todos los equipos funcionan correctamente', 3, 'Pendiente', '2025-05-07 13:28:13', '2025-05-07 13:28:17', 1),
(152, 85, 'Preparar caja', 'Preparar la caja registradora con cambio', 4, 'Pendiente', '2025-05-07 13:28:13', '2025-05-07 13:28:18', 1),
(153, 85, 'Limpieza inicial', 'Realizar limpieza rápida del área de atención', 5, 'Pendiente', '2025-05-07 13:28:13', NULL, NULL),
(154, 97, 'Revisión de inventario', 'Comprobar niveles de inventario', 1, 'Pendiente', '2025-05-07 13:33:22', '2025-05-07 13:33:43', 1),
(155, 97, 'Limpieza de áreas comunes', 'Mantener áreas comunes limpias', 2, 'Pendiente', '2025-05-07 13:33:22', NULL, NULL),
(156, 97, 'Control de temperatura', 'Verificar temperaturas de equipos', 3, 'Pendiente', '2025-05-07 13:33:22', NULL, NULL),
(157, 93, 'Revisión de inventario', 'Comprobar niveles de inventario', 1, 'Pendiente', '2025-05-07 14:25:16', NULL, NULL),
(158, 93, 'Limpieza de áreas comunes', 'Mantener áreas comunes limpias', 2, 'Pendiente', '2025-05-07 14:25:16', NULL, NULL),
(159, 93, 'Control de temperatura', 'Verificar temperaturas de equipos', 3, 'Pendiente', '2025-05-07 14:25:16', NULL, NULL),
(160, 105, 'Cerrar caja', 'Realizar cierre y conteo de caja', 1, 'Completada', '2025-05-08 13:11:02', '2025-05-08 13:11:30', 1),
(161, 105, 'Limpieza de cierre', 'Limpieza general del local', 2, 'Completada', '2025-05-08 13:11:02', '2025-05-08 13:11:34', 1),
(162, 105, 'Apagar equipos', 'Apagar todos los equipos electrónicos', 3, 'Completada', '2025-05-08 13:11:02', '2025-05-08 13:11:36', 1),
(163, 105, 'Apagar luces', 'Apagar todas las luces', 4, 'Completada', '2025-05-08 13:11:02', '2025-05-08 13:11:37', 1),
(164, 105, 'Activar alarma', 'Activar sistema de alarma al salir', 5, 'Completada', '2025-05-08 13:11:02', '2025-05-08 13:11:38', 1),
(165, 100, 'Revisión de inventario', 'Comprobar niveles de inventario', 1, 'Completada', '2025-05-08 13:11:50', '2025-05-08 13:11:51', 1),
(166, 100, 'Limpieza de áreas comunes', 'Mantener áreas comunes limpias', 2, 'Pendiente', '2025-05-08 13:11:50', NULL, NULL),
(167, 100, 'Control de temperatura', 'Verificar temperaturas de equipos', 3, 'Pendiente', '2025-05-08 13:11:50', NULL, NULL),
(168, 101, 'Desactivar alarma', 'Desactivar sistema de alarma al llegar', 1, 'Completada', '2025-05-08 14:23:12', '2025-05-08 14:23:52', 1),
(169, 101, 'Encender luces', 'Encender todas las luces del local', 2, 'Pendiente', '2025-05-08 14:23:12', NULL, NULL),
(170, 101, 'Verificar equipos', 'Comprobar que todos los equipos funcionan correctamente', 3, 'Pendiente', '2025-05-08 14:23:12', NULL, NULL),
(171, 101, 'Preparar caja', 'Preparar la caja registradora con cambio', 4, 'Pendiente', '2025-05-08 14:23:12', NULL, NULL),
(172, 101, 'Limpieza inicial', 'Realizar limpieza rápida del área de atención', 5, 'Pendiente', '2025-05-08 14:23:12', NULL, NULL),
(173, 98, 'Desactivar alarma', 'Desactivar sistema de alarma al llegar', 1, 'Pendiente', '2025-05-08 14:28:31', NULL, NULL),
(174, 98, 'Encender luces', 'Encender todas las luces del local', 2, 'Pendiente', '2025-05-08 14:28:31', NULL, NULL),
(175, 98, 'Verificar equipos', 'Comprobar que todos los equipos funcionan correctamente', 3, 'Pendiente', '2025-05-08 14:28:31', NULL, NULL),
(176, 98, 'Preparar caja', 'Preparar la caja registradora con cambio', 4, 'Pendiente', '2025-05-08 14:28:31', NULL, NULL),
(177, 98, 'Limpieza inicial', 'Realizar limpieza rápida del área de atención', 5, 'Pendiente', '2025-05-08 14:28:31', NULL, NULL),
(178, 99, 'Cerrar caja', 'Realizar cierre y conteo de caja', 1, 'Pendiente', '2025-05-08 14:36:30', NULL, NULL),
(179, 99, 'Limpieza de cierre', 'Limpieza general del local', 2, 'Pendiente', '2025-05-08 14:36:30', NULL, NULL),
(180, 99, 'Apagar equipos', 'Apagar todos los equipos electrónicos', 3, 'Pendiente', '2025-05-08 14:36:30', NULL, NULL),
(181, 99, 'Apagar luces', 'Apagar todas las luces', 4, 'Pendiente', '2025-05-08 14:36:30', NULL, NULL),
(182, 99, 'Activar alarma', 'Activar sistema de alarma al salir', 5, 'Pendiente', '2025-05-08 14:36:30', NULL, NULL),
(183, 108, 'MODO NOCHE MÁQUINAS YOGUR', 'Poner máquinas de yogur en modo noche, se deben poner las máquinas de yogur en modo noche, realizando una FOTO de las temperaturas.', 1, 'Pendiente', '2025-05-08 15:00:38', NULL, NULL),
(184, 108, 'GUARDAR + TAPAR TOPPING', 'Guardar topping frutas en el frigo. Tapar toppings del mostrador. Cerrar las bolsas de topping indicando fecha de apertura. Se deben adjuntar las imágenes - FOTO topping guardado.', 2, 'Pendiente', '2025-05-08 15:00:38', NULL, NULL),
(185, 108, 'LIMPIEZA MOSTRADOR', 'Se debe hacer una limpieza del mostrador. Adjuntar imágenes de la zona en perfecto estado: - FOTO del mostrador, cubetas, y vitrinas del cristal limpias.', 3, 'Pendiente', '2025-05-08 15:00:38', NULL, NULL),
(186, 108, 'LIMPIEZA GENERAL', 'Se debe efectuar una limpieza de maquinarias de: - Maquinaria Sweet - Granizadoras - Utensilios de cocina - Mobiliario - Local - WC. Se deben adjuntar las siguientes imágenes: FOTO maquinaria sweet, FOTO granizadoras, FOTO utensilios de cocina, FOTO mobiliario, FOTO local, FOTO WC.', 4, 'Pendiente', '2025-05-08 15:00:38', NULL, NULL),
(187, 108, 'CIERRE CAJA', 'Se debe efectuar el cierre de la caja. Se debe realizar \"Z ciega\" en el TPV. Adjuntar FOTO sobre el cierre completado.', 5, 'Pendiente', '2025-05-08 15:00:38', NULL, NULL),
(188, 110, 'MODO NOCHE MÁQUINAS YOGUR', 'Poner máquinas de yogur en modo noche, se deben poner las máquinas de yogur en modo noche, realizando una FOTO de las temperaturas.', 1, 'Pendiente', '2025-05-12 09:04:20', NULL, NULL),
(189, 110, 'GUARDAR + TAPAR TOPPING', 'Guardar topping frutas en el frigo. Tapar toppings del mostrador. Cerrar las bolsas de topping indicando fecha de apertura. Se deben adjuntar las imágenes - FOTO topping guardado.', 2, 'Pendiente', '2025-05-12 09:04:20', NULL, NULL),
(190, 110, 'LIMPIEZA MOSTRADOR', 'Se debe hacer una limpieza del mostrador. Adjuntar imágenes de la zona en perfecto estado: - FOTO del mostrador, cubetas, y vitrinas del cristal limpias.', 3, 'Pendiente', '2025-05-12 09:04:20', NULL, NULL),
(191, 110, 'LIMPIEZA GENERAL', 'Se debe efectuar una limpieza de maquinarias de: - Maquinaria Sweet - Granizadoras - Utensilios de cocina - Mobiliario - Local - WC. Se deben adjuntar las siguientes imágenes: FOTO maquinaria sweet, FOTO granizadoras, FOTO utensilios de cocina, FOTO mobiliario, FOTO local, FOTO WC.', 4, 'Pendiente', '2025-05-12 09:04:20', NULL, NULL),
(192, 110, 'CIERRE CAJA', 'Se debe efectuar el cierre de la caja. Se debe realizar \"Z ciega\" en el TPV. Adjuntar FOTO sobre el cierre completado.', 5, 'Pendiente', '2025-05-12 09:04:20', NULL, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tarea_comentarios`
--

CREATE TABLE `tarea_comentarios` (
  `id` int(11) NOT NULL,
  `tarea_id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `comentario` text NOT NULL,
  `fecha_creacion` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `tarea_comentarios`
--

INSERT INTO `tarea_comentarios` (`id`, `tarea_id`, `usuario_id`, `comentario`, `fecha_creacion`) VALUES
(8, 53, 2, 'coñete', '2025-04-11 11:20:12'),
(13, 95, 1, 'pene', '2025-04-30 12:59:53'),
(14, 106, 1, 'hola', '2025-05-05 09:40:51'),
(15, 122, 1, 'ya está', '2025-05-06 12:06:04');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tarea_imagenes`
--

CREATE TABLE `tarea_imagenes` (
  `id` int(11) NOT NULL,
  `tarea_id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `ruta_imagen` varchar(255) NOT NULL,
  `nombre_imagen` varchar(255) NOT NULL,
  `fecha_subida` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `tarea_imagenes`
--

INSERT INTO `tarea_imagenes` (`id`, `tarea_id`, `usuario_id`, `ruta_imagen`, `nombre_imagen`, `fecha_subida`) VALUES
(6, 53, 2, 'uploads/tarea_53/20250411_111945_JPEG_20250411_111917_6717782373562698524.jpg', '20250411_111945_JPEG_20250411_111917_6717782373562698524.jpg', '2025-04-11 11:19:45'),
(8, 52, 1, 'uploads/tarea_52/20250411_134500_JPEG_20250411_134455_7913040357863442576.jpg', '20250411_134500_JPEG_20250411_134455_7913040357863442576.jpg', '2025-04-11 13:45:00'),
(9, 51, 1, 'uploads/tarea_51/20250411_140401_JPEG_20250411_140355_5274315018157315369.jpg', '20250411_140401_JPEG_20250411_140355_5274315018157315369.jpg', '2025-04-11 14:04:01'),
(15, 95, 1, 'uploads/tarea_95/20250430_125946_JPEG_20250430_125943_7034134086390231245.jpg', '20250430_125946_JPEG_20250430_125943_7034134086390231245.jpg', '2025-04-30 12:59:46'),
(16, 106, 1, 'uploads/tarea_106/20250505_094043_JPEG_20250505_094027_6163194153990068462.jpg', '20250505_094043_JPEG_20250505_094027_6163194153990068462.jpg', '2025-05-05 09:40:43'),
(19, 117, 1, 'uploads/tarea_117/20250506_103433_JPEG_20250506_103427_1303380101439373376.jpg', '20250506_103433_JPEG_20250506_103427_1303380101439373376.jpg', '2025-05-06 10:34:33'),
(20, 117, 1, 'uploads/tarea_117/20250506_103522_JPEG_20250506_103510_2497135516777272912.jpg', '20250506_103522_JPEG_20250506_103510_2497135516777272912.jpg', '2025-05-06 10:35:22'),
(21, 122, 1, 'uploads/tarea_122/20250506_120546_JPEG_20250506_120537_4157692146492184051.jpg', '20250506_120546_JPEG_20250506_120537_4157692146492184051.jpg', '2025-05-06 12:05:46');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `ID` int(11) NOT NULL,
  `Nombre` varchar(255) DEFAULT NULL,
  `usuario` varchar(255) DEFAULT NULL,
  `Contraseña` varchar(255) DEFAULT NULL,
  `Rol` enum('Admin','Area Manager','Store Manager','RRHH','Staff') DEFAULT NULL,
  `apellido` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`ID`, `Nombre`, `usuario`, `Contraseña`, `Rol`, `apellido`) VALUES
(1, 'Admin', 'AdminSMOOY', '$2b$12$09JDpsqoZun4upakQmBE7.RhlRVaPJRuN8OmECIgVEdIy7OE5BnSu', 'Admin', 'admin'),
(2, 'Staff', 'StaffSMOOY', '$2b$12$05AniiXG4nMOt67UG6ueSu552/pIDGrnBC6LJ6/ezAPh7F5w091y6', 'Staff', 'staff'),
(19, 'AreaManagerSMOOY', 'AreaManagerSMOOY', '$2b$12$bWGyemmphTp06Rh28Q5mW.lBzECqUJnXn110wEVAL2sSkps.Eq52m', 'Area Manager', 'AreaManager'),
(24, 'Store', 'StoreManagerSMOOY', 'SMOOY', 'Store Manager', 'Manager');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario_establecimiento`
--

CREATE TABLE `usuario_establecimiento` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) DEFAULT NULL,
  `establecimiento_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuario_establecimiento`
--

INSERT INTO `usuario_establecimiento` (`id`, `usuario_id`, `establecimiento_id`) VALUES
(1, 2, 1),
(2, 1, 2),
(6, 1, 1),
(32, 19, 1),
(33, 19, 2),
(35, 24, 15);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `avisos`
--
ALTER TABLE `avisos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `establecimiento_id` (`establecimiento_id`),
  ADD KEY `usuario_id` (`usuario_id`);

--
-- Indices de la tabla `aviso_comentarios`
--
ALTER TABLE `aviso_comentarios`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `aviso_imagenes`
--
ALTER TABLE `aviso_imagenes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_ai_aviso` (`aviso_id`),
  ADD KEY `fk_ai_usuario` (`usuario_id`);

--
-- Indices de la tabla `establecimientos`
--
ALTER TABLE `establecimientos`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `procesos2`
--
ALTER TABLE `procesos2`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_establecimiento_id` (`establecimiento_id`);

--
-- Indices de la tabla `proceso_comentarios`
--
ALTER TABLE `proceso_comentarios`
  ADD PRIMARY KEY (`id`),
  ADD KEY `proceso_id` (`proceso_id`),
  ADD KEY `usuario_id` (`usuario_id`);

--
-- Indices de la tabla `proceso_imagenes`
--
ALTER TABLE `proceso_imagenes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `proceso_id` (`proceso_id`),
  ADD KEY `usuario_id` (`usuario_id`);

--
-- Indices de la tabla `proceso_tareas`
--
ALTER TABLE `proceso_tareas`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_tarea_proceso` (`proceso_id`),
  ADD KEY `fk_tarea_usuario` (`usuario_completado_id`);

--
-- Indices de la tabla `tarea_comentarios`
--
ALTER TABLE `tarea_comentarios`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_tc_tarea` (`tarea_id`),
  ADD KEY `fk_tc_usuario` (`usuario_id`);

--
-- Indices de la tabla `tarea_imagenes`
--
ALTER TABLE `tarea_imagenes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_ti_tarea` (`tarea_id`),
  ADD KEY `fk_ti_usuario` (`usuario_id`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`ID`);

--
-- Indices de la tabla `usuario_establecimiento`
--
ALTER TABLE `usuario_establecimiento`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`),
  ADD KEY `establecimiento_id` (`establecimiento_id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `avisos`
--
ALTER TABLE `avisos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=39;

--
-- AUTO_INCREMENT de la tabla `aviso_comentarios`
--
ALTER TABLE `aviso_comentarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `aviso_imagenes`
--
ALTER TABLE `aviso_imagenes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT de la tabla `establecimientos`
--
ALTER TABLE `establecimientos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;

--
-- AUTO_INCREMENT de la tabla `procesos2`
--
ALTER TABLE `procesos2`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=111;

--
-- AUTO_INCREMENT de la tabla `proceso_comentarios`
--
ALTER TABLE `proceso_comentarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT de la tabla `proceso_imagenes`
--
ALTER TABLE `proceso_imagenes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT de la tabla `proceso_tareas`
--
ALTER TABLE `proceso_tareas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=193;

--
-- AUTO_INCREMENT de la tabla `tarea_comentarios`
--
ALTER TABLE `tarea_comentarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT de la tabla `tarea_imagenes`
--
ALTER TABLE `tarea_imagenes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=22;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=42;

--
-- AUTO_INCREMENT de la tabla `usuario_establecimiento`
--
ALTER TABLE `usuario_establecimiento`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=42;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `avisos`
--
ALTER TABLE `avisos`
  ADD CONSTRAINT `avisos_ibfk_1` FOREIGN KEY (`establecimiento_id`) REFERENCES `establecimientos` (`id`),
  ADD CONSTRAINT `avisos_ibfk_2` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`ID`);

--
-- Filtros para la tabla `aviso_imagenes`
--
ALTER TABLE `aviso_imagenes`
  ADD CONSTRAINT `fk_ai_aviso` FOREIGN KEY (`aviso_id`) REFERENCES `avisos` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_ai_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`ID`);

--
-- Filtros para la tabla `procesos2`
--
ALTER TABLE `procesos2`
  ADD CONSTRAINT `fk_establecimiento_id` FOREIGN KEY (`establecimiento_id`) REFERENCES `establecimientos` (`id`) ON DELETE SET NULL;

--
-- Filtros para la tabla `proceso_comentarios`
--
ALTER TABLE `proceso_comentarios`
  ADD CONSTRAINT `fk_pc_proceso` FOREIGN KEY (`proceso_id`) REFERENCES `procesos2` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_pc_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`ID`);

--
-- Filtros para la tabla `proceso_imagenes`
--
ALTER TABLE `proceso_imagenes`
  ADD CONSTRAINT `fk_pi_proceso` FOREIGN KEY (`proceso_id`) REFERENCES `procesos2` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_pi_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`ID`);

--
-- Filtros para la tabla `proceso_tareas`
--
ALTER TABLE `proceso_tareas`
  ADD CONSTRAINT `fk_tarea_proceso` FOREIGN KEY (`proceso_id`) REFERENCES `procesos2` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_tarea_usuario` FOREIGN KEY (`usuario_completado_id`) REFERENCES `usuarios` (`ID`);

--
-- Filtros para la tabla `tarea_comentarios`
--
ALTER TABLE `tarea_comentarios`
  ADD CONSTRAINT `fk_tc_tarea` FOREIGN KEY (`tarea_id`) REFERENCES `proceso_tareas` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_tc_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`ID`);

--
-- Filtros para la tabla `tarea_imagenes`
--
ALTER TABLE `tarea_imagenes`
  ADD CONSTRAINT `fk_ti_tarea` FOREIGN KEY (`tarea_id`) REFERENCES `proceso_tareas` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_ti_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`ID`);

--
-- Filtros para la tabla `usuario_establecimiento`
--
ALTER TABLE `usuario_establecimiento`
  ADD CONSTRAINT `usuario_establecimiento_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`ID`),
  ADD CONSTRAINT `usuario_establecimiento_ibfk_2` FOREIGN KEY (`establecimiento_id`) REFERENCES `establecimientos` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
