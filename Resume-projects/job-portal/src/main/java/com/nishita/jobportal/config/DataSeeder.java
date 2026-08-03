package com.nishita.jobportal.config;
import com.nishita.jobportal.entity.*;
import com.nishita.jobportal.repository.*;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.crypto.password.PasswordEncoder;
@Configuration public class DataSeeder{
 @Bean CommandLineRunner seed(UserRepository users,CandidateProfileRepository profiles,CompanyRepository companies,JobRepository jobs,PasswordEncoder encoder){return args->{if(users.count()>0)return;UserAccount recruiter=user("Jordan Lee","recruiter@example.com",Role.RECRUITER,encoder);users.save(recruiter);UserAccount candidate=user("Maya Patel","candidate@example.com",Role.CANDIDATE,encoder);users.save(candidate);CandidateProfile profile=new CandidateProfile();profile.setUser(candidate);profile.setHeadline("Computer Science student");profile.setLocation("Madison, WI");profile.setSkills("Java, Spring Boot, SQL, JavaScript");profiles.save(profile);Company company=new Company();company.setName("Northstar Labs");company.setWebsite("https://example.com");company.setLocation("Chicago, IL");company.setDescription("A fictional product engineering company building practical software.");company.setRecruiter(recruiter);companies.save(company);jobs.save(job(company,"Software Engineering Intern","Chicago, IL · Hybrid","Internship","Java, Spring Boot, REST APIs, SQL","Join a product engineering team to build and test customer-facing services.",24,30));jobs.save(job(company,"Data Platform Intern","Remote","Internship","Python, SQL, PostgreSQL, ETL","Help improve reliable data workflows and internal analytics tools.",23,29));};}
 private UserAccount user(String name,String email,Role role,PasswordEncoder encoder){UserAccount u=new UserAccount();u.setName(name);u.setEmail(email);u.setRole(role);u.setPasswordHash(encoder.encode("Password123!"));return u;}
 private JobPosting job(Company c,String title,String location,String type,String skills,String description,int min,int max){JobPosting j=new JobPosting();j.setCompany(c);j.setTitle(title);j.setLocation(location);j.setEmploymentType(type);j.setSkills(skills);j.setDescription(description);j.setSalaryMin(min);j.setSalaryMax(max);return j;}
}
