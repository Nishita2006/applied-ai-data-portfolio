package com.nishita.jobportal.service;
import com.nishita.jobportal.dto.ProfileDtos.*;
import com.nishita.jobportal.entity.*;
import com.nishita.jobportal.exception.NotFoundException;
import com.nishita.jobportal.repository.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import java.io.IOException;
import java.nio.file.*;
import java.util.*;
@Service public class ProfileService{
 private final CandidateProfileRepository profiles; private final CompanyRepository companies;
 @Value("${app.upload-dir}") private String uploadDir;
 public ProfileService(CandidateProfileRepository p,CompanyRepository c){profiles=p;companies=c;}
 public ProfileResponse get(UserAccount u){return response(profile(u));}
 public ProfileResponse update(UserAccount u,ProfileRequest r){CandidateProfile p=profile(u);p.setHeadline(r.headline());p.setLocation(r.location());p.setBio(r.bio());p.setSkills(r.skills());return response(profiles.save(p));}
 public ProfileResponse resume(UserAccount u,MultipartFile file){if(file.isEmpty()||file.getOriginalFilename()==null)throw new IllegalArgumentException("Choose a resume file");String original=Paths.get(file.getOriginalFilename()).getFileName().toString();String lower=original.toLowerCase();if(!(lower.endsWith(".pdf")||lower.endsWith(".doc")||lower.endsWith(".docx")))throw new IllegalArgumentException("Resume must be PDF, DOC, or DOCX");try{Path dir=Paths.get(uploadDir);Files.createDirectories(dir);String stored=u.getId()+"-"+UUID.randomUUID()+lower.substring(lower.lastIndexOf('.'));Files.copy(file.getInputStream(),dir.resolve(stored),StandardCopyOption.REPLACE_EXISTING);CandidateProfile p=profile(u);p.setResumePath(stored);return response(profiles.save(p));}catch(IOException e){throw new IllegalArgumentException("Resume could not be stored");}}
 public CompanyResponse createCompany(UserAccount u,CompanyRequest r){if(r.name()==null||r.name().isBlank())throw new IllegalArgumentException("Company name is required");Company c=new Company();c.setRecruiter(u);c.setName(r.name());c.setWebsite(r.website());c.setLocation(r.location());c.setDescription(r.description());c=companies.save(c);return new CompanyResponse(c.getId(),c.getName(),c.getWebsite(),c.getLocation(),c.getDescription());}
 public java.util.List<CompanyResponse> companies(UserAccount u){return companies.findByRecruiterId(u.getId()).stream().map(c->new CompanyResponse(c.getId(),c.getName(),c.getWebsite(),c.getLocation(),c.getDescription())).toList();}
 private CandidateProfile profile(UserAccount u){return profiles.findByUserId(u.getId()).orElseThrow(()->new NotFoundException("Candidate profile not found"));}
 private ProfileResponse response(CandidateProfile p){return new ProfileResponse(p.getUser().getName(),p.getUser().getEmail(),p.getHeadline(),p.getLocation(),p.getBio(),p.getSkills(),p.getResumePath());}
}
