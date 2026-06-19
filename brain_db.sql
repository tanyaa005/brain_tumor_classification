-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 24, 2026 at 10:20 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `brain_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `auth_users`
--

CREATE TABLE `auth_users` (
  `id` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  `role` int(11) NOT NULL DEFAULT 2,
  `status` int(11) NOT NULL DEFAULT 0,
  `created_on` timestamp NOT NULL DEFAULT current_timestamp(),
  `created_by` varchar(100) DEFAULT NULL,
  `updated_on` timestamp NULL DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `auth_users`
--

INSERT INTO `auth_users` (`id`, `username`, `email`, `password`, `role`, `status`, `created_on`, `created_by`, `updated_on`, `updated_by`) VALUES
(1, 'ravi', 'tiwari.ravi1@gmail.com', '$2b$12$VhOxg7RiR/68ZCjNw.hHQuw1t4PEVvEfoQDpTE/w1UYm7pjAeXl0e', 1, 1, '2026-04-21 07:29:34', NULL, NULL, NULL),
(2, 'raj', 'raj@gmail.com', '$2b$12$vzwwktBXjs5TAO.uCba10OuFohzcYBEy6qqg3xYu1xU4Gj/RYnLiC', 2, 1, '2026-04-21 08:32:10', NULL, NULL, NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `auth_users`
--
ALTER TABLE `auth_users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `auth_users`
--
ALTER TABLE `auth_users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
